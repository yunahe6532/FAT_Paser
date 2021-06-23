import struct
import time
start1 = time.time()

def convert_bytes(obyte):           # One Byte to int
    return struct.unpack_from("B", obyte)[0]

def convert_word(tbytes):           # Two Byte to int
    return struct.unpack_from("H", tbytes)[0]

def convert_dword(fbytes):          # Four Byte to int
    return struct.unpack_from("I", fbytes)[0]

def convert_dwordlong(ebytes):      # Eight Byte to int
    return struct.unpack_from("Q", ebytes)[0]

PartitionTypes = {
    0x00: "Empty",
    0x01: "FAT12,CHS",
    0x04: "FAT16 16-32MB,CHS",
    0x05: "Microsoft Extended",
    0x06: "FAT16 32MB,CHS",
    0x07: "NTFS",
    0x0b: "FAT32,CHS",
    0x0c: "FAT32,LBA",
    0x0e: "FAT16, 32MB-2GB,LBA",
    0x0f: "Microsoft Extended, LBA",
    0x11: "Hidden FAT12,CHS",
    0x14: "Hidden FAT16,16-32MB,CHS",
    0x16: "Hidden FAT16,32MB-2GB,CHS",
    0x1b: "Hidden FAT32,CHS",
    0x1c: "Hidden FAT32,LBA",
    0x1e: "Hidden FAT16,32MB-2GB,LBA",
}

def StrSectorSzie(num):
    str_size = ['B', 'KB', 'MB', 'GB']
    t = size = (num * 512.)
    for i in range(4):
        t = t / 1024
        if int(t) > 0:
            size = size / 1024
        else:
            break
    return ('%.2f %s' % (size, str_size[i]))

def PrintDATAarea(DATA,AL,NO):
    start1 = time.time()
    
    return start1
    

def PrintFATarea(data,end):
    start1 = time.time()
    i=8
    cluster = []
    cluster2 = []
    bcluster = []
    index = 0
    index2 = 0
    x = 512
    while i<(end*x): ##Fat Size * 512 
        flag = 0
        if data[i:i+4] == b'\xff\xff\xff\x0f': # data 가 파일 끝이면
           if int(i/4) not in cluster2:             
                cluster.append([])
                cluster[index].append(int(i/4))
                index += 1     
           i += 4
        elif data[i:i+4] == b'\x00\x00\x00\x00':    #data가 Non-Allocated 라면
            bcluster.append([])
            bcluster[index2].append(int(i/4))  
            i += 4 
            while i<(end*x):
                if data[i:i+4] == b'\x00\x00\x00\x00':
                    bcluster[index2].append(int(i/4))               #Non-Allocated 리스트 추가
                    i += 4 
                else:
                    index2 += 1
                    break
        else: # re.search('......00',data[j:j+4].hex()): #만약 data가 다음 클러스터를 나타내면
            cluster.append([]) #cluster list에 [] 추가
            cluster[index].append(int(i/4)) #cluster[index] 번째 리스트에 현재 클러스터 저장
            j = convert_dword(data[i:i+4])*4  #data가 나타내는 다음 클러스터 번호를 j 에 저장
            if (convert_dword(data[j:j+4])*4) != j+4: #만약 j 다음 클러스터가 2 이상 차이나면
                flag = 1
            while i<(end*x):
                if data[j:j+4] == b'\xff\xff\xff\x0f': # data 가 파일 끝이면
                    i += 4
                    if flag == 1:
                        flag = 0
                        if int(j/4) in cluster2:
                            break
                        else:
                            cluster[index].append(int(j/4))
                            cluster2.append(int(j/4))
                            index +=1
                            break
                    else:
                        cluster[index].append(int(j/4))
                        index += 1
                        break   
                else: #만약 data가 다음 클러스터를 나타내면
                    if (convert_dword(data[j:j+4])*4) == j+4 and flag == 0:
                        cluster[index].append(int(j/4))
                        j = convert_dword(data[j:j+4])*4      #j에 다음 클러스터를 번호 저장
                        i = j
                    else:
                        flag = 1                
                        cluster[index].append(int(j/4))
                        j = convert_dword(data[j:j+4])*4       #j에 다음 클러스터를 번호 저장
    start1 = time.time() - start1
    return cluster, bcluster, start1

def PrintFSINFO(PSINFO):
    PSINFO_data = []
    NumClustr = convert_word(PSINFO[0x1E8:0x1EB])
    StartClustr = convert_dword(PSINFO[0x1EC:0x1F0])
    PSINFO_data.extend([NumClustr,StartClustr])
    return PSINFO_data
def PrintVBR(VBR):
    VBR_data = []
    OEMID = VBR[3:11].decode()
    BytePerSector = convert_word(VBR[0x0B:0x0D])
    SectorPerCluster = convert_bytes(VBR[0x0D:0x0E])
    ReservedArea = convert_word(VBR[0x0E:0x10])
    FATnum = convert_bytes(VBR[0x10:0x11])
    FATsize = convert_dword(VBR[0x24:0x28])
    TotalSector = convert_dword(VBR[0x20:0x24])
    VolumeLable = VBR[0x47:0x52].decode()
    VolumeID = format((struct.unpack('<I', VBR[0x43:0x47])[0]),'X')
    VBR_data.extend([OEMID,BytePerSector,SectorPerCluster,ReservedArea,FATnum,FATsize,TotalSector,VolumeLable,VolumeID])
    return VBR_data
         
def PrintMBR(part):
    MBR = []
    BootFlag = part[0:1].hex()
    Num = convert_dword(part[12:12 + 4]) 
    PartType = PartitionTypes[convert_bytes(part[4:5])] #부팅 가능여부
    PartStartSector = convert_dword(part[8:8 + 4]) #파티션 시작 섹터  
    SectorSize = StrSectorSzie(Num) #섹터 크기
    PartSize = Num
    MBR.extend([BootFlag,PartType,PartStartSector,SectorSize,PartSize])
    return MBR

def ReadDATA(i,start,total):
    start1 = time.time()
    f.seek(start*512)
    data = f.read(0x200*total)
    return data, start1

def ReadFATarea(i,VBR,part):
    start1 = time.time()
    f.seek((VBR[i][3]+part)*512)
    data = f.read(0x200*VBR[i][5])
    #print(data[0:4])
    if data[0x00:0x04] == b'\xf8\xff\xff\x0f':
        start1 = time.time() - start1
        return data,start1
    else:
        print('Read FATarea Fail')

def ReadFSINFO(start):
    start1 = time.time()
    f.seek(start*512)
    data = f.read(0x200)
    if data[0x00:0x04] == b'RRaA' and data[0x1E4:0x1E8] == b'rrAa':
        #print('FSINFO Read Sucess')
        start1 = time.time() - start1
        return data,start1
    else:
        print('Read FSINFO Fail')

def ReadVBR(start):
    start1 = time.time()
    f.seek(start*512)
    data = f.read(0x200)
    if data[0x03:0x0A] == b'MSDOS5.':
        #print('VBR Read Sucess')
        start1 = time.time() - start1
        return data,start1
    else:
        print('Read VBR Fail')

def ReadMBR(mbr):
    start1 = time.time()
    if mbr[510] == 0x55 and mbr[511] == 0xAA: #mbr 체크
        print('MBR Read Sucess\n')
        # 파티션 정보 획득
        part = [] 
        for i in range(0,4):
            if (mbr[0x1BE + (i * 0x10):0x1BE + (i * 0x10) + 0x10]) != b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': #예외처리
                part.append(mbr[0x1BE + (i * 0x10):0x1BE + (i * 0x10) + 0x10])
            else:
               continue
        start1 = time.time() - start1
        return part, start1
    else:
        print('Read MBR Fail')
        
if __name__ == '__main__':
    f = open("sample7.vhd", "rb")
    file = f.read()
    mbr = file[0x00:0x200]
    part,st1 = ReadMBR(mbr)
    mbr_data = []
    vbr_data = []
    FSINFO_data = []
    FATarea_data = []
    NonAllocated_data = []
    #print(mbr)
    for i in range(0,len(part)):
        p = part[i]
        if p != 0x0c:
            mbr_data.append(PrintMBR(p))
            #print(mbr_data)
            print('--------- Partition %d ---------' % (i+1))
            print('---Boot flag : 0x%s' % mbr_data[i][0])
            print('---Partition Type : %s' % mbr_data[i][1])
            print('---Partition Starting Sector : %d Sector' % mbr_data[i][2])
            print('---SectorSize : %s' % mbr_data[i][3])
            print('---partition size : %d Sector\n' % mbr_data[i][4])
            
            VBR,st2 = ReadVBR(mbr_data[i][2])
            vbr_data.append(PrintVBR(VBR))
            print('--------- Partition %d VBR INFO ---------' % (i+1))
            print('---OEM ID = %s' % vbr_data[i][0])
            print('---Byte Per Sector = %s Bytes' % vbr_data[i][1])
            print('---Sector Per Cluster = %s Sector' % vbr_data[i][2])
            print('---Reserved Area = %s Sector' % vbr_data[i][3])
            print('---FAT num = %s' % vbr_data[i][4])
            print('---FAT size = %s Sector' % vbr_data[i][5])
            print('---Total Sector = %s Sector' % vbr_data[i][6])
            print('---Volume Lable = %s' % vbr_data[i][7])
            print('---Volume ID = %s-%s' % (vbr_data[i][8][i:4],vbr_data[i][8][4:8]))
            
            FSINFO,st3 = ReadFSINFO(mbr_data[i][2]+1)
            FSINFO_data.append(PrintFSINFO(FSINFO))
            print('--------- File System Information %d ---------' % (i+1))
            print('---Number Of Free Clusters = %d Cluster' % FSINFO_data[i][0])
            print('---Next Free Clusters = %d Cluster\n' % FSINFO_data[i][1])
            
            FATarea,st4 = ReadFATarea(i,vbr_data,mbr_data[i][2])
            Allocated, NonAll,st5 = PrintFATarea(FATarea,vbr_data[i][5])
            FATarea_data.append(Allocated)
            NonAllocated_data.append(NonAll)
            print('--------- FAT Area %d ---------' % (i+1))
            print("Allocated Cluister :",FATarea_data[i])
            #print("Non-Allocated Cluister :",NonAllocated_data[i])
            
            DATA_AREA, st6 = ReadDATA(i,(mbr_data[i][2]+vbr_data[i][3]+vbr_data[i][5]*2),vbr_data[i][6])
            #PT_DATA_AREA.append(PrintDATAarea(DATA_AREA,Allocated,NonAll))
            
        else:
            print('FAT32가 아닙니다.\n')

f.close()
print("MBR time :", st1)
print("VBR time :", st2)
print("FSINFO time :", st3)
print("Read FAT time :",st4)
print("Print FAT time :",st5)
#print("Read DATA time :",st6)
print("total time :", time.time() - start1)
