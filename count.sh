#!/bin/bash

awk '{if (match($8,/'"A"'/) && match($7,/'"C"'/) ){print}}' hit.txt > cat > count_AtoC.txt
numAtoC=$(cat count_AtoC.txt | wc -l)
echo "number of A to C count: $numAtoC"
echo "AtoC	$numAtoC" > count_table.txt 
awk '{if (match($8,/'"A"'/) && match($7,/'"G"'/) ){print}}' hit.txt > cat > count_AtoG.txt
numAtoG=$(cat count_AtoG.txt | wc -l)
echo "number of A to G count: $numAtoG"
echo "AtoG	$numAtoG" >> count_table.txt
awk '{if (match($8,/'"A"'/) && match($7,/'"T"'/) ){print}}' hit.txt > cat > count_AtoT.txt
numAtoT=$(cat count_AtoT.txt | wc -l)
echo "number of A to T count: $numAtoT"
echo "AtoT	$numAtoT" >> count_table.txt
awk '{if (match($8,/'"C"'/) && match($7,/'"A"'/) ){print}}' hit.txt > cat > count_CtoA.txt
numCtoA=$(cat count_CtoA.txt | wc -l)
echo "number of C to A count: $numCtoA"
echo "CtoA	$numCtoA" >> count_table.txt
awk '{if (match($8,/'"C"'/) && match($7,/'"G"'/) ){print}}' hit.txt > cat > count_CtoG.txt
numCtoG=$(cat count_CtoG.txt | wc -l)
echo "number of C to G count: $numCtoG"
echo "CtoG	$numCtoG" >> count_table.txt
awk '{if (match($8,/'"C"'/) && match($7,/'"T"'/) ){print}}' hit.txt > cat > count_CtoT.txt
numCtoT=$(cat count_CtoT.txt | wc -l)
echo "number of C to T count: $numCtoT"
echo "CtoT	$numCtoT" >> count_table.txt
awk '{if (match($8,/'"G"'/) && match($7,/'"A"'/) ){print}}' hit.txt > cat > count_GtoA.txt
numGtoA=$(cat count_GtoA.txt | wc -l)
echo "number of G to A count: $numGtoA"
echo "GtoA	$numGtoA" >> count_table.txt
awk '{if (match($8,/'"G"'/) && match($7,/'"C"'/) ){print}}' hit.txt > cat > count_GtoC.txt
numGtoC=$(cat count_GtoC.txt | wc -l)
echo "number of G to C count: $numGtoC"
echo "GtoC	$numGtoC" >> count_table.txt
awk '{if (match($8,/'"G"'/) && match($7,/'"T"'/) ){print}}' hit.txt > cat > count_GtoT.txt
numGtoT=$(cat count_GtoT.txt | wc -l)
echo "number of G to T count: $numGtoT"
echo "GtoT	$numGtoT" >> count_table.txt
awk '{if (match($8,/'"T"'/) && match($7,/'"A"'/) ){print}}' hit.txt > cat > count_TtoA.txt
numTtoA=$(cat count_TtoA.txt | wc -l)
echo "number of T to A count: $numTtoA"
echo "TtoA	$numTtoA" >> count_table.txt
awk '{if (match($8,/'"T"'/) && match($7,/'"C"'/) ){print}}' hit.txt > cat > count_TtoC.txt
numTtoC=$(cat count_TtoC.txt | wc -l)
echo "number of T to C count: $numTtoC"
echo "TtoC	$numTtoC" >> count_table.txt
awk '{if (match($8,/'"T"'/) && match($7,/'"G"'/) ){print}}' hit.txt > cat > count_TtoG.txt
numTtoG=$(cat count_TtoG.txt | wc -l)
echo "number of T to G count: $numTtoG"
echo "TtoG	$numTtoG" >> count_table.txt
