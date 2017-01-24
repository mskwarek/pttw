@echo on

::call 01_binary_src_dst\
::call 02_coder\
::call 03_spreader\
::call 04_qpsk_mod\
call 05_ofdm_mod\ --f "dane.txt" --sc 2 --p 2 --fsize 100 --action "modulate"
call 06_awgn\awgn.exe --src input_awgn --dst output_awgn --snr 30
::call 07_fast_fading\
call 05_ofdm_mod\ --f "ms.txt" --sc 2 --p 2 --fsize 100 --action "demodulate"
::call 04_qpsk_mod\
::call 03_spreader\
::call 02_coder\
::call 01_binary_src_dst\