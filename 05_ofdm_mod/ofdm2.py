import numpy as np
import argparse

def read_file_data(filename):
    with open(filename, 'r') as f:
        return list(f.read())

def parse_read_data(filedata):

    filedata = map(int,filedata)
    real_list = []
    imag_list = []
    counter = 0
    for n,i in enumerate(filedata):
        if i == 0:
            filedata[n]=-1
    for sign in filedata:
        if counter%2 == 0:
            real_list.append(sign)
        else:
            imag_list.append(sign)
        counter+=1
    return np.asarray(real_list), np.asarray(imag_list), filedata

def modulate_signal(real_part, imag_part, no_carriers, num_ofdm_symbols):

    input_signal = real_part+1j*imag_part
    num_symbols = input_signal.size
    num_ofdm_symbols = (int(np.ceil(float(num_symbols) /
                                        no_carriers)))    
    input_signal = np.hstack(
        [input_signal, np.zeros(no_carriers * num_ofdm_symbols - num_symbols)])
    input_signal.shape = (num_ofdm_symbols, no_carriers)
    return input_signal

def add_pilots(parallel_signal):

    temp = parallel_signal
    symbols = parallel_signal.shape[0]
    carriers = parallel_signal.shape[1]
    pilot = np.zeros(symbols, dtype=complex)
    idx_pilots = []
    #print symbols, pilot
    
    if carriers < 10:
        idx_pilot = carriers /2
        #print idx_pilot
        temp = np.insert(temp, idx_pilot, pilot, axis=1)
        idx_pilots.append(idx_pilot)

    elif carriers > 10 and carriers < 50:
        idx_pilot = carriers / 2
        idx_pilot2 = idx_pilot / 2
        idx_pilot3 = idx_pilot + idx_pilot2
        temp = np.insert(temp, idx_pilot + 1, pilot, axis=1)
        temp = np.insert(temp, idx_pilot2, pilot, axis=1)
        temp = np.insert(temp, idx_pilot3 + 2 , pilot, axis=1)
        idx_pilots.append([idx_pilot, idx_pilot2, idx_pilot3])

    else:
        idx_pilot = carriers / 2
        idx_pilot2 = idx_pilot / 2
        idx_pilot3 = idx_pilot + idx_pilot2
        idx_pilot4 = idx_pilot2 / 2
        idx_pilot5 = idx_pilot3 + idx_pilot4
        
        temp = np.insert(temp, idx_pilot + 1, pilot, axis=1)
        temp = np.insert(temp, idx_pilot2, pilot, axis=1)
        temp = np.insert(temp, idx_pilot3 + 2 , pilot, axis=1)
        temp = np.insert(temp, idx_pilot4 + 3 , pilot, axis=1)
        temp = np.insert(temp, idx_pilot5 + 4 , pilot, axis=1)
        idx_pilots.append([idx_pilot, idx_pilot2, idx_pilot3,
                           idx_pilot4, idx_pilot5])
    return temp, idx_pilots
        

def add_ifft(parallel_signal):

    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    t = np.empty((symbols, subcarriers), dtype=complex)
    
    for i in range(0, parallel_signal.shape[0]):
        t[i] = np.fft.ifftn(parallel_signal[i])
    #print t
    #for j in t:
    #    print np.fft.fftn(j)
    return t

def add_prefixes(parallel_signal, prefix_size):

    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    t = np.empty((symbols, subcarriers+prefix_size), dtype=complex)
    
    prefix_zeros = np.zeros(prefix_size)
    for i in range(0, parallel_signal.shape[0]):
        tt = np.concatenate((prefix_zeros, parallel_signal[i]), axis=0)
        t[i] = tt        
    return t

def remove_pilots(parallel_signal, pilots):
    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    temp = np.empty((symbols, subcarriers), dtype=complex)
    temp = np.delete(parallel_signal, pilots, axis=1)
    return temp

def remove_prefixes(parallel_signal, prefix_size):

    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    t = np.empty((symbols, subcarriers-prefix_size), dtype=complex)
    for i in range(0, parallel_signal.shape[0]):
        tt = parallel_signal[i][prefix_size:]
        t[i] = tt        
    return t

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, required=True, dest='action')
    parser.add_argument('--f', type=str, required=True, dest='f')
    parser.add_argument('--sc', type=int, required=True, dest='sc')
    parser.add_argument('--p', type=int, required=True, dest='p')
    #parser.add_argument('--fsize', type=int, required=True, dest='fsize')
    return parser.parse_args()


def write_signal(filename, signal):
    formatted = [str(signal[i]) for i in range(0, len(signal))]
    with open(filename, 'w+') as fi:
        fi.write("\n".join(formatted))
    
if __name__ == '__main__':

    if parse_arguments().action == 'modulate':
        filedata = read_file_data(parse_arguments().f)
        real_list, imag_list, blank_data = parse_read_data(filedata)
        parallel_signals = modulate_signal(real_list, imag_list, parse_arguments().sc,  2)

        signal_with_ifft = add_ifft(parallel_signals)
        signal_with_pilots, idx_pilots= add_pilots(signal_with_ifft)
        signal_with_prefixes = add_prefixes(signal_with_pilots, parse_arguments().p)

        write_signal('modulated_signal.txt', signal_with_prefixes)
        

