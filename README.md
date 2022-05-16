# Kawal C1

![Logo](http://kawalc1.org/static/img/logo-kotak.png)

For a description of how this software was used to verify the results of the 2019
Indonesian elections, read the information at [Kawal Pemilu](https://github.com/kawalpemilu/upload.kawalpemilu.org).
This video contains almost all tally forms from the 2019 presidential elections as they were digitized by our system:

[![IMAGE ALT TEXT](http://img.youtube.com/vi/_cgl1tMVcJ0/0.jpg)](http://www.youtube.com/watch?v=_cgl1tMVcJ0 "800.000 Formulir")
Our [facebook group](https://www.facebook.com/c1kawal/) will post irregular updates.

# Verifikasi Otomatis Formulir Pemilu C1

Deskripsi Use Case:
 1. Pengguna mengunggah formulir C1
 1. Aplikasi akan mencoba mengenali angka pada formulir 
 1. Angka hasil pendeteksian akan ditampilkan beserta dengan hasil penjumlahannya
 1. Jika pengguna telah memverifikasi dan setuju dengan hasil pendeteksian, proses selesai.
 1. Jika ditemukan hasil pendeteksian yang tidak sesuai, pengguna dapat melakukan koreksi secara manual.
 1. Semua data akan disimpan di database dan digunakan untuk peningkatan akurasi dari algoritma yang digunakan.

# Automatic Verification of C1 Election Forms

Use Case Description:
 1. The user uploads a C1 form
 1. The application tries to recognize the numbers 
 1. The numbers that it has detected and whether they add up are displayed
 1. If the user agrees with what the computer has detected the process is finished. 
 1. If the user doesn't agree with the computer, he/she has the opportunity to submit the correct numbers.
 1. All this data is stored in a database and can serve to improve the accuracy of the algorithms.


## Development setup - python

To run unittests
 1. copy the example.env file to pycharm.env
 1. adjust the BASEDIR to point to your project location
 1. install [envfile](https://plugins.jetbrains.com/plugin/7861-envfile) plugin in PyCharm; follow the instructions
 1. run the unittests from the Run menu; they will fail, but you will have configuration
 1. edit the unittest configuration via the Run menu; point the unittest configuration to the pycharm.env file you just created
 1. run the unittests again, they should now succeed.
