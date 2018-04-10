COMMONSRC=$(wildcard linstor/proto/*.proto)
JAVASRC=$(wildcard linstor/proto/javainternal/*.proto)
COMMONNOEND=$(COMMONSRC:.proto=)
JAVANOEND=$(COMMONNOEND) $(JAVASRC:.proto=)
COMMONDRBDOPTS=drbdoptions.json

PYOUT=../
PYSUFF=_pb2.py
PYS=$(patsubst %,$(PYOUT)/%$(PYSUFF),$(COMMONNOEND))
PYCONSTS=../linstor/sharedconsts.py
PYPROPS=../linstor/properties.py
PYDRBDOPTS=../linstor/drbdsetup_options.py

JAVAOUT=../src/com/linbit
JAVASUFF=OuterClass.java
JAVAS=$(patsubst %,$(JAVAOUT)/%$(JAVASUFF),$(JAVANOEND))
JAVACONSTS=../src/com/linbit/linstor/api/ApiConsts.java

# make java the default one
all: java

%.proto:
	;

%.json:
	;

$(PYOUT)/%$(PYSUFF): %.proto
	protoc -I=. --python_out=$(PYOUT) $<

$(JAVAOUT)/%$(JAVASUFF): %.proto
	protoc -I=. --java_out=../src $<

$(PYCONSTS): consts.json
	./genconsts.py python > $@

$(PYPROPS): properties.json $(COMMONDRBDOPTS)
	./genproperties.py python properties.json $(COMMONDRBDOPTS) > $@

$(PYDRBDOPTS):
	./gendrbdoptions.py $(COMMONDRBDOPTS) $@

$(COMMONDRBDOPTS):
	./gendrbdoptions.py $(COMMONDRBDOPTS)

$(JAVACONSTS): consts.json
	./genconsts.py java > $@

python: $(PYS) $(PYCONSTS) $(PYPROPS) $(PYDRBDOPTS)

java: $(JAVAS) $(JAVACONSTS) $(COMMONDRBDOPTS)

cleanpython:
	rm -f $(PYS) $(PYCONSTS) $(PYPROPS)

cleanjava:
	rm -f $(JAVAS) $(JAVACONSTS)

clean: cleanpython cleanjava
	rm -f $(COMMONDRBDOPTS)
