#!/usr/bin/bash

# Creat: 11-01-2025
# @author: rafael
# @description: Convierte texto a audio

source ~/bin/colors

# paràmetres
[ "$1" == "sencer" ] && sencer=true
declare -a escenes=()

if [ $sencer ]; then
   echo -e "${BG_CYN}Es convertirà l'arxiu sencer${C_NONE}"
elif [ ${#1} -gt 0 ]; then
   escenes+=($1)
   echo -e "${BG_CYN}Es convertiran les escenes indicades:${C_NONE}${CB_WHT} ${escenes[@]}${C_NONE}"
else
   escenes+=("106" "107" "108" "109" "111" "112" "201" "202" "203" "204" "205" "207")
   echo -e "${BG_CYN}Es convertiran (per defecte) aquestes escenes:${C_NONE}${CB_WHT} ${escenes[@]}${C_NONE}"
fi

# paràmetres TTS
model_name="tts_models/ca/custom/vits"

# variables locals
LF="\n"
BL=" "
CC=": "
FragmentVeu="casats"
baseDir=$(pwd)
dirSortida="sortides/casats/wav/"
baseArxiuWav="${baseDir}/${dirSortida}"
[ $sencer ] && baseArxiu="casats" || baseArxiu="casats-escena-"
ArxiuWav=""

Personatges=('Joan':'02689'
             'Pompeu':'01591'
             'Canut':'02452'
             'Justa':'mar'
             'Tina':'00762'
             'Gisela':'jan'
             'Mar':'pau'
             'Emma':'ona')
Narrador='pep'

function get_id_personatge() {
   #@type $1: string; nom del personatge
   #@type $2: string; id del narrador
   pat_nom="$1:(.*)"
   for p in ${Personatges[@]}; do
      if [[ $p =~ $pat_nom ]]; then break; fi
   done
   #echo ${p#:*}   #retorna el id de veu eliminant el nom
   if [ ${#BASH_REMATCH[1]} -gt 0 ]; then
      echo ${BASH_REMATCH[1]};
   else
      echo $2;
   fi
}

function is_personatge() {
   #@type $1: string; nom del personatge
   pat_nom="$1:.*"
   for p in ${Personatges[@]}; do
      if [[ $p =~ $pat_nom ]]; then trobat=true; break; fi
   done
   echo $trobat   #retorna true si el paràmetre rebut és un nom de personatge
}

function elimina_fragments() {
   echo -e "${BG_CYN}Fi de l'escena ${1}${C_NONE}\n"
   rm "${baseArxiuWav}casats_[0-9]*.wav"
   #cd $baseArxiuWav
   #for file in "${baseArxiuWav}casats_[0-9]*.wav"; do
   #   rm "$file"
   #done
   #cd $baseDir
}

function nom_arxiu() {
   num=$(printf "%04d" $1)
   echo "${dirSortida}${FragmentVeu}_${num}.wav"
}

function mostra_sentencia() {
   if [[ $(is_personatge "$1") == true ]]; then
      if [[ "$1" == "Joan" ]]; then
         ini_color=$CB_YLW
      else
         ini_color=$CB_CYN
      fi
   else
      if [[ ${1:0:6} == "Casats" ||
            ${1:0:11} == "Acte Primer" ||
            ${1:0:10} == "Acte Segon" ||
            ${1:0:11} == "Acte Tercer" ||
            ${1:0:10} == "Acte Quart" ||
            ${1:0:12} == "Primera Part" ||
            ${1:0:11} == "Segona Part" ||
            ${1:0:6} == "Escena" ||
            ${1:0:4} == "Teló" ]]
      then
         ini_color=$BG_CYN
      else
         ini_color=$C_NONE
      fi
   fi
   echo -e "$ini_color${1}${C_NONE}${2}"
}

function fragment_text_to_audio() {
   #@type $1: string; text que es tracta
   #@type $2: int; número seqüencial per a la generació del nom d'arxiu de sortida
   #@type $3: string; id de veu
   #@type $4: string; caracter de finalització de echo

   mostra_sentencia "$1" "$4";
   ((n=$2+1));

   if [[ "$4" != "${CC}" ]]; then
      #if [[ "$4" == "${CC}" && ($1 != "Erni" || $sencer) ]]; then return; fi
      #if [[ $1 == "Erni" && $sencer ]]; then $1="parla l'$1"; fi

      # Run TTS
      tts --text "${1}" --model_name "${model_name}" --speaker_idx "${3}" --out_path "$(nom_arxiu $n)" 2>/dev/null
   fi
   return $n;
}

function proces() {
   escena=$1
   arxiu=$baseArxiu$escena;
   ArxiuWav="baseArxiuWav${arxiu}.wav";
   if [ -f $ArxiuWav ]; then rm $ArxiuWav; fi
   ArxiuEntrada="entrades/${arxiu}.txt";

   while IFS= read -r sentencia
   do
      echo -e "Sentència:.$sentencia.${#sentencia}";

      if [ ${#sentencia} -gt 0 ]; then
         # extraer el personaje [1] y el texto [3]
         [[ $sentencia =~ $pattern_person ]];

         if [ ${#BASH_REMATCH[0]} -gt 0 ]; then
            persona=${BASH_REMATCH[1]};
            text=${BASH_REMATCH[3]};
            fragment_text_to_audio "$persona" $n $Narrador "${CC}"; n=$?;

            id_veu=$(get_id_personatge $persona $Narrador);

            # extraer, del texto [3], los comentarios del narrador
            [[ $text =~ $pattern_narrador ]]
            if [ ${BASH_REMATCH[0]} ]; then
               if [ ${BASH_REMATCH[1]} && ${BASH_REMATCH[2]} && ${BASH_REMATCH[3]} ]; then
                  fragment_text_to_audio "${BASH_REMATCH[1]}" $n $id_veu "${BL}"; n=$?;
                  fragment_text_to_audio "${BASH_REMATCH[2]}" $n $Narrador "${BL}"; n=$?;
                  fragment_text_to_audio "$part3" $n $id_veu "${BL}"; n=$?;
               elif [ ${BASH_REMATCH[1]} && ${BASH_REMATCH[2]} ]; then
                  fragment_text_to_audio "${BASH_REMATCH[1]}" $n $id_veu "${BL}"; n=$?;
                  fragment_text_to_audio "${BASH_REMATCH[2]}" $n $Narrador "${BL}"; n=$?;
               elif [ ${BASH_REMATCH[2]} && ${BASH_REMATCH[3]} ]; then
                  fragment_text_to_audio "${BASH_REMATCH[2]}" $n $Narrador "${BL}"; n=$?;
                  fragment_text_to_audio "${BASH_REMATCH[3]}" $n $id_veu "${LF}"; n=$?;
               fi
            else
               fragment_text_to_audio "$text" $n $id_veu "${LF}"; n=$?;
            fi
         else
            fragment_text_to_audio "${sentencia}" $n $Narrador "${LF}"; n=$?;
         fi
      fi
   done < $ArxiuEntrada

   if [ -z $sencer ]; then elimina_fragments $escena; fi
}
# ------------------------------
# principal
# ------------------------------
pattern_person="^(\w*?\s?)(:\s?)(.*$)"
pattern_narrador="([^\(]*)(\(.*?\))(.*)"

n=0;

if [ $sencer ]; then
   proces
else
   for escena in ${escenes[@]}; do
      proces $escena
   done
fi
