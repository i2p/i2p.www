TMP=/tmp/findpochanges$$.txt
TMP2=newtranslations.txt
rm -f $TMP2
touch $TMP2
for i in i2p2www/translations/*/*/*.po
do
	if [ -d ./.git ]; then
		git diff $i | grep '+msgstr' | grep -v '+msgstr ""' > $TMP
	else
		mtn diff $i | grep '+msgstr' | grep -v '+msgstr ""' > $TMP
	fi
	if [ -s $TMP ]
	then
		echo $i >> $TMP2
		echo $i
		cat $TMP
		echo
	fi
done
echo 'New strings in the following files:'
cat $TMP2
rm -f $TMP
