#!/bin/bash
#
# Tratamiento de los archivos de audio de un directorio
#
source ~/bin/colores

base=$PWD/sortides/teràpies/wav_pyttsx3

function IgualarFrecuencias() {
   audio_files=$1
	for f in $(ls $audio_files); do
		 echo $f
	    if sox -r 2250 -e unsigned -b 16 -c 1 "$f" "$f.resampled"; then
		     # This way we will only replace the original file with the
		     # resampled version if sox returns a zero (no error) error code.
	        mv "$f.resampled" "$f"
	    else
	        soxerrno = $?
	        echo "Sox reported error number $soxerrno while processing file $f"
	    fi
	done
}

function UnirAudios() {
   audio_files=$1
	output=$2
	output_tmp=$3
	n=0
	for f in $(ls $audio_files); do
		#let n++; if [[ "$n" == "100" ]]; then break; fi
		echo $f
		sox --magic -V1 -q --single-threaded --norm -v1 $output $f $output_tmp
		mv -f $output_tmp $output
	done
}

echo -e "${CB_MAG}+-----------------------------------------------------------------------------+"
echo -e "|                                    MENÚ                                     |"
echo -e "+-----------------------------------------------------------------------------+"
echo -e "| 1. Unir los archivos .wav de audio                                          |"
echo -e "| 2. Igualar la frecuencia de muestreo (sample-rate) de los archivos de audio |"
echo -e "| 3. Salir                                                                    |"
echo -e "+-----------------------------------------------------------------------------+${CB_WHT}"
read -p "Escoge una opción: " -r -n1 resp
echo -e "${C_NONE}"

case $resp in
	1) echo "Unir los archivos .wav de audio"
		UnirAudios $base/*.wav $base/teràpies.wav $base/tmp.wav
		;;
	2) echo "Igualar la frecuencia de muestreo (sample-rate) de los archivos de audio"
		IgualarFrecuencias $base/*.wav
		;;
	3) exit
		;;
esac
