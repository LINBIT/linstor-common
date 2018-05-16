COMMONSRC=$(wildcard linstor/proto/*.proto) $(wildcard linstor/proto/eventdata/*.proto)
JAVASRC=$(wildcard linstor/proto/javainternal/*.proto)
COMMONNOEND=$(COMMONSRC:.proto=)
JAVANOEND=$(COMMONNOEND) $(JAVASRC:.proto=)
COMMONDRBDOPTS=drbdoptions.json
COMMONPROPERTIES=properties.json
PROTOC=protoc

PYOUT=../
PYSUFF=_pb2.py
PYS=$(patsubst %,$(PYOUT)/%$(PYSUFF),$(COMMONNOEND))
PYCONSTS=../linstor/sharedconsts.py
PYPROPS=../linstor/properties.py
PYDRBDOPTS=../linstor/drbdsetup_options.py

JAVABASEOUT=../generated-src
JAVAOUT=$(JAVABASEOUT)/com/linbit
JAVASUFF=OuterClass.java
JAVAS=$(patsubst %,$(JAVAOUT)/%$(JAVASUFF),$(JAVANOEND))
JAVAAPIOUT=$(JAVAOUT)/linstor/api
JAVACONSTS=$(JAVAAPIOUT)/ApiConsts.java
JAVAPROPERTYRULES=../src/com/linbit/linstor/api/prop/GeneratedPropertyRules.java

# make java the default one
all: java

%.proto:
	;

%.json:
	;

$(PYOUT)/%$(PYSUFF): %.proto
	${PROTOC} -I=. --python_out=$(PYOUT) $<

$(JAVABASEOUT):
	mkdir $@

$(JAVAOUT)/%$(JAVASUFF): %.proto $(JAVABASEOUT)
	${PROTOC} -I=. --java_out=$(JAVABASEOUT) $<

$(PYCONSTS): consts.json
	./genconsts.py python > $@

$(JAVAPROPERTYRULES): $(COMMONPROPERTIES) $(COMMONDRBDOPTS)
	./genproperties.py java $(COMMONPROPERTIES) $(COMMONDRBDOPTS) > $@

$(PYPROPS): $(COMMONPROPERTIES) $(COMMONDRBDOPTS)
	./genproperties.py python $(COMMONPROPERTIES) $(COMMONDRBDOPTS) > $@

$(PYDRBDOPTS):
	./gendrbdoptions.py $(COMMONDRBDOPTS) $@

$(COMMONDRBDOPTS):
	./gendrbdoptions.py $(COMMONDRBDOPTS)

$(JAVAAPIOUT):
	mkdir -p $@

$(JAVACONSTS): consts.json $(JAVAAPIOUT)
	./genconsts.py java > $@

python: $(PYS) $(PYCONSTS) $(PYPROPS) $(PYDRBDOPTS)

java: $(JAVAS) $(JAVACONSTS) $(COMMONDRBDOPTS) $(JAVAPROPERTYRULES)

cleanpython:
	rm -f $(PYS) $(PYCONSTS) $(PYPROPS) $(PYDRBDOPTS)

cleanjava:
	rm -f $(JAVAS) $(JAVACONSTS)
	rm -Rf $(JAVABASEOUT)

clean: cleanpython cleanjava
	rm -f $(COMMONDRBDOPTS)
