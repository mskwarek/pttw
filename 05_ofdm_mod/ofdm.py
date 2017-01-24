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
    print input_signal.shape 
    return input_signal

def add_pilots(parallel_signal):

    temp = parallel_signal
    symbols = parallel_signal.shape[0]
    carriers = parallel_signal.shape[1]
    pilot = np.zeros(symbols, dtype=complex)

    if carriers < 10:
        idx_pilot = carriers /2
        temp = np.insert(temp, idx_pilot, pilot, axis=1)
        return temp, [idx_pilot]
    elif carriers > 10 and carriers < 50:
        idx_pilot = carriers / 2
        idx_pilot2 = idx_pilot / 2
        idx_pilot3 = idx_pilot + idx_pilot2
        temp = np.insert(temp, idx_pilot, pilot, axis=1)
        temp = np.insert(temp, idx_pilot2, pilot, axis=1)
        temp = np.insert(temp, idx_pilot3, pilot, axis=1)
        return temp, [idx_pilot+1, idx_pilot2, idx_pilot3+2]
    else:
        idx_pilot = carriers / 2
        idx_pilot2 = idx_pilot / 2
        idx_pilot3 = idx_pilot + idx_pilot2
        idx_pilot4 = idx_pilot2 / 2
        idx_pilot5 = idx_pilot3 + idx_pilot4
        temp = np.insert(temp, idx_pilot, pilot, axis=1)
        temp = np.insert(temp, idx_pilot2, pilot, axis=1)
        temp = np.insert(temp, idx_pilot3, pilot, axis=1)
        temp = np.insert(temp, idx_pilot4, pilot, axis=1)
        temp = np.insert(temp, idx_pilot5, pilot, axis=1)
        return temp, [idx_pilot+2, idx_pilot2+1, idx_pilot3+3, idx_pilot4, idx_pilot5 +4]
        
def remove_pilots(parallel_signal, pilots):
    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    temp = np.empty((symbols, subcarriers), dtype=complex)
    temp = np.delete(parallel_signal, pilots, axis=1)
    return temp

def write_pilots(filename, pilots):
   with open(filename, 'w+') as fi:
        for a in pilots:
            fi.write(str(a) + "\n")

def read_pilots(filename):
    with open(filename) as f:
        lines = [line.rstrip('\n') for line in f]
    return map(int,lines)

def add_ifft(parallel_signal):
    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    t = np.empty((symbols, subcarriers), dtype=complex)
    for i in range(0, parallel_signal.shape[0]):
        t[i] = np.fft.ifftn(parallel_signal[i])
    return t

def add_prefixes(parallel_signal, prefix_size):
    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    t = np.empty((symbols, subcarriers+prefix_size), dtype=complex)
    
    prefix_zeros = np.zeros(prefix_size)
    for i in range(0, parallel_signal.shape[0]):
        t[i] = np.concatenate((prefix_zeros, parallel_signal[i]), axis=0)       
    return t

def remove_prefixes(parallel_signal, prefix_size):
    symbols = parallel_signal.shape[0]
    subcarriers = parallel_signal.shape[1]
    t = np.empty((symbols, subcarriers-prefix_size), dtype=complex)
    for i in range(0, parallel_signal.shape[0]):
        t[i] = parallel_signal[i][prefix_size:]        
    return t

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, required=True, dest='action')
    parser.add_argument('--f', type=str, required=True, dest='f')
    parser.add_argument('--sc', type=int, required=True, dest='sc')
    parser.add_argument('--p', type=int, required=True, dest='p')
    parser.add_argument('--fsize', type=int, required=True, dest='fsize')
    return parser.parse_args()

def write_signal(filename, signal):
    formatted = [str(signal[i]) for i in range(0, len(signal))]
    with open(filename, 'w+') as fi:
        fi.write("\n".join(formatted))

def write_signal2(filename, signal):
    with open(filename, 'w+') as fi:
        for _list in signal:
            for _string in _list:
                fi.write(str(_string) + "\n")
            #fi.write(",\n")

def load_complex_data(filename, subcarriers, len_prefix, len_pilots):
    with open(filename) as f:
        lines = [line.rstrip('\n') for line in f]
        content = f.readlines()
        complex_arr = []
        symbols = len(lines) / (subcarriers + len_prefix + len_pilots)
        carriers = (subcarriers + len_prefix + len_pilots)
        tt = np.empty((symbols,carriers), dtype=complex) # spoko
        for i in range(0,symbols):
            temp = []
            for j in lines[i*carriers:(i+1)*carriers]:
                temp.append(complex(j))
            tt[i] = temp    
        return tt  
        
def demodulate_signal(modulated_signal, subcarriers, num_ofdm_symbols):
    temp = np.empty((modulated_signal.shape[0],modulated_signal.shape[1]),dtype=complex)
    counter = 0
    for i in modulated_signal:
        temp[counter] = np.fft.fftn(i)
        counter+=1
    ordered_tab = []
    for j in temp:
        for k in j:
            ordered_tab.append(k.real)
            ordered_tab.append(k.imag)
    parsed_tab = np.hstack(ordered_tab)
    t = []
    for i in parsed_tab:
        t.append(int(round(i)))
    for l in range(0,len(ordered_tab)):
        if t[l] == -1:
            t[l] = 0
    return t
        
if __name__ == '__main__':

    ###########################################################################
    #
    # Arguments description:
    #    --f "filename.txt"
    #    --action "action" values : "modulate", "demodulate"
    #    --sc integer_value : number of subcarriers
    #    --p integer_value : size of pilot
    #    --fsize integer_value : size of ifft window
    #
    ###########################################################################

    if parse_arguments().action == 'modulate':
        filedata = read_file_data(parse_arguments().f)
        real_list, imag_list, blank_data = parse_read_data(filedata)
        parallel_signals = modulate_signal(real_list, imag_list, parse_arguments().sc, parse_arguments().fsize)

        signal_with_ifft = add_ifft(parallel_signals)
        signal_with_pilots, idx_pilots= add_pilots(signal_with_ifft)
        signal_with_prefixes = add_prefixes(signal_with_pilots, parse_arguments().p)

        write_signal2('ms.txt', signal_with_prefixes)
        write_signal('modulated_signal.txt', signal_with_prefixes)
        write_pilots('pilots.txt', idx_pilots)
    else:
        idx_pilots = read_pilots('pilots.txt')
        filedata = load_complex_data(parse_arguments().f, parse_arguments().sc, parse_arguments().p, len(idx_pilots))
        signal_without_prefixes = remove_prefixes(filedata, parse_arguments().p)
        signal_without_pilots = remove_pilots(signal_without_prefixes, idx_pilots)

        demodulated_signal = demodulate_signal(signal_without_pilots, parse_arguments().sc, parse_arguments().fsize)

        string_signal = ''.join(str(e) for e in map(int,demodulated_signal))
        with open('demodulated_signal.txt', 'w+') as fi:
            fi.write(string_signal)
        
        
        

