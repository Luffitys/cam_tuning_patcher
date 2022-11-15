#/usr/bin/env python3

import os
import shutil

patches = [
	{
        'patchname':            'Disable Luma Noise Reduction',
        'lookup':               'anr10_ipe', #SEARCHES THIS STRING
        'dataoffset':           0xC0, #hex; offset from file beginning to data section offset
        'offset':               0x27, #hex; offset from anr10_ipe to its data section offset
        'blockoffset':          0x98, #offset from anr10_ipe data section to (HIGH_PASS) luma noise reduction
        'original':             '01', #hex without '0x'
        'modified':             '00', #hex without '0x'
	},
	{
        'patchname':            'Disable Edge Detection (ENTIRELY)',
        'lookup':               'asf30_ipe', #SEARCHES THIS STRING
        'dataoffset':           0xC0, #hex; offset from file beginning to data section offset
        'offset':               0x27, #hex; offset from asf30_ipe to its data section offset
        'blockoffset':          0x0, #hex without '0x'; offset from asf30_ipe data section to // (start of data section)
        'original':             '01', #hex without '0x'
        'modified':             '00', #hex without '0x'
	},
	{
        'patchname':            'Disable Edge Detection (layer 1)',
        'lookup':               'asf30_ipe', #SEARCHES THIS STRING
        'dataoffset':           0xC0, #hex; offset from file beginning to data section offset
        'offset':               0x27, #hex; offset from asf30_ipe to its data section offset
        'blockoffset':          0xC8, #hex without '0x'; offset from asf30_ipe data section to layer_1 section
        'original':             '01', #hex without '0x'
        'modified':             '00', #hex without '0x'
	},
	{
        'patchname':            'Disable Edge Detection (layer 2)',
        'lookup':               'asf30_ipe', #SEARCHES THIS STRING
        'dataoffset':           0xC0, #hex; offset from file beginning to data section offset
        'offset':               0x27, #hex; offset from asf30_ipe to its data section offset
        'blockoffset':          0xD0, #hex without '0x'; offset from asf30_ipe data section to layer_2 section
        'original':             '01', #hex without '0x'
        'modified':             '00', #hex without '0x'
	},
	{
        'patchname':            'Disable Edge Detection (radial)',
        'lookup':               'asf30_ipe', #SEARCHES THIS STRING
        'dataoffset':           0xC0, #hex; offset from file beginning to data section offset
        'offset':               0x27, #hex; offset from asf30_ipe to its data section offset
        'blockoffset':          0xD8, #hex without '0x'; offset from asf30_ipe data section to radial section
        'original':             '01', #hex without '0x'
        'modified':             '00', #hex without '0x'
	},
	{
        'patchname':            'Disable Edge Detection (contrast)',
        'lookup':               'asf30_ipe', #SEARCHES THIS STRING
        'dataoffset':           0xC0, #hex; offset from file beginning to data section offset
        'offset':               0x27, #hex; offset from asf30_ipe to its data section offset
        'blockoffset':          0xE0, #hex without '0x'; offset from asf30_ipe data section to contrast section
        'original':             '01', #hex without '0x'
        'modified':             '00', #hex without '0x'
	},
]

def patch_start(patches=None):
    filename = input('\nEnter the full file name of your tuning .bin\nExample: com.qti.tuned.umi_semco_s5khmx.bin\n------\n: ')

    #backup original file
    if os.path.exists(filename + '.bak') == False:
        shutil.copyfile(filename, filename + '.bak')

    print('\nFollowing patches are available:\n')
    num=0

    #list all patches
    for patch in patches:
        print('(' + str(num) + ') ' + '[' + patch['patchname'] + ' ' + '(' +  patch['lookup'] + ')' + ']')
        num=num+1

    #patch selection input
    str_arr = input('\nEnter your desired patch(es). Separated by comma(s) (,). Or type all (all). (e.g. 0,1): ')

    #convert string input to integer list
    if str_arr != 'all':
        str_arr = str_arr.split(',')
        patch_arr = list(map(int, str_arr))
    else:
        i=0
        patch_arr = []
        for patch in patches:
            patch_arr.append(i)
            i=i+1

    #execute patching process for each selected patch
    for n in patch_arr:
        patch_process(filename, n)

    #avoid exit without user input
    print("\nPatches have been applied!\n\nPress Enter to exit ...")
    input()

#convert hex x86 to arm. or other way around idk
def hex_to_big_little_int(hex):
    little_hex = bytearray.fromhex(hex)
    little_hex.reverse()
    str_little = ''.join(format(x, '02x') for x in little_hex)
    int_little = int(str_little,base=16)
    return int_little

def patch_process(filename, n):
    with open(filename, 'r+b') as f:
        for index, patch in enumerate(patches):
            #checks if current list index is selected to be patched by user
            if index == n:
                f.seek(0)
                data = f.read()
                #counts all string search hits
                num_hit = data.count(str.encode(patch['lookup']))
                print('\n' + '[' + patch['lookup'] + ']' + ' has been found ' + str(num_hit) +  ' times: ')
                count=0
                matches=0
                #goes to offset which contains data section offset
                f.seek(patch['dataoffset'])
                #read the data section offset
                datasectionoffset = hex_to_big_little_int(f.read(4).hex())
                print('data section offset int32: ' + str(datasectionoffset) + '\n')
                #goes back to file beginning
                f.seek(0)
                #repeats until break
                while True:
                    #save current location for later use
                    location = f.tell()
                    string = patch['lookup'].encode('utf-8')
                    #checks for current patching hit. avoids infinite while True: loop from never stopping
                    if f.read(len(string)).hex() == string.hex() and count < num_hit:
                        print('found ' + patch['lookup'] + ' (' + patch['patchname'] + ')' + '!')
                        #save current location for later use
                        location = f.tell()
                        #go from patch['lookup'] to offset that stores the data block offset
                        f.seek(f.tell() + patch['offset'])
                        #read the lookup data block offset
                        offset = f.read(4).hex()
                        #convert offset hex to int
                        offset_little_int = hex_to_big_little_int(offset)
                        print('offset hex: ' + offset)
                        print('offset int32: ' + str(offset_little_int))
                        #go to lookup data block and go to offset that has to be patched
                        f.seek(offset_little_int + datasectionoffset)
                        print (patch['lookup'] + ' block offset int32: ' + str(f.tell()))
                        f.read(patch['blockoffset'])
                        #save offset for later use
                        new_offset = f.tell()
                        print('value offset from file beginning int32: ' + str(new_offset))
                        print('value: ' + f.read(len(patch['original'])//2).hex())
                        #go back to previous location
                        f.seek(new_offset)
                        #checks if original byte == patch['original'] byte
                        if f.read(len(patch['original'])//2).hex() == patch['original']:
                            #go back to previous location
                            f.seek(new_offset)
                            #patch byte(s)
                            f.write(bytes.fromhex(patch['modified']))
                            #go back to previous location
                            f.seek(new_offset)
                            print('new value: ' + str(f.read(len(patch['modified'])//2).hex()))
                            matches += 1
                        #goes back to origin location
                        f.seek(location)
                        print(' ')
                        count += 1
                    elif count < num_hit:
                        #goes one byte or whatever further than the last hit, to prevent patching the same hit infinite times
                        f.seek(location + 1)
                    #checks if all hits have been patched
                    elif count >= num_hit:
                        #close the patched file
                        f.close()
                        print('\n(Patched ' + str(matches) + ' hits!)')
                        break

def main():
    patch_start(patches=patches)

if __name__ == '__main__':
    main()
