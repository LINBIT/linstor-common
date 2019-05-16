COMMONSRC=$(wildcard linstor/proto/*.proto)  $(wildcard linstor/proto/common/*.proto) $(wildcard linstor/proto/eventdata/*.proto)  $(wildcard linstor/proto/requests/*.proto) $(wildcard linstor/proto/responses/*.proto)
JAVASRC=$(wildcard linstor/proto/javainternal/*.proto) $(wildcard linstor/proto/javainternal/c2s/*.proto) $(wildcard linstor/proto/javainternal/s2c/*.proto)
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

JAVABASEOUT=../server/generated-src
JAVAOUT=$(JAVABASEOUT)/com/linbit
JAVASUFF=OuterClass.java
JAVAS=$(patsubst %,$(JAVAOUT)/%$(JAVASUFF),$(JAVANOEND))
JAVAAPIOUT=$(JAVAOUT)/linstor/api
JAVACONSTS=$(JAVAAPIOUT)/ApiConsts.java
JAVAPROPOUT=$(JAVAAPIOUT)/prop
JAVAPROPERTYRULES=$(JAVAPROPOUT)/GeneratedPropertyRules.java

GOCONSTS=../apiconsts.go

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

$(PYCONSTS): genconsts.py consts.json
	./genconsts.py python > $@

$(JAVAPROPOUT):
	mkdir -p $@

$(JAVAPROPERTYRULES): genproperties.py $(COMMONPROPERTIES) $(COMMONDRBDOPTS) $(JAVAPROPOUT)
	./genproperties.py java $(COMMONPROPERTIES) $(COMMONDRBDOPTS) > $@

$(PYPROPS): genproperties.py $(COMMONPROPERTIES) $(COMMONDRBDOPTS)
	./genproperties.py python $(COMMONPROPERTIES) $(COMMONDRBDOPTS) > $@

$(COMMONDRBDOPTS): gendrbdoptions.py
	./gendrbdoptions.py $(COMMONDRBDOPTS)

$(JAVAAPIOUT):
	mkdir -p $@

$(JAVACONSTS): genconsts.py consts.json $(JAVAAPIOUT)
	./genconsts.py java > $@

$(GOCONSTS): genconsts.py consts.json
	./genconsts.py golang | gofmt > $@

pythonproto: $(PYS)

python: $(PYCONSTS) $(PYPROPS)

java: $(JAVAS) $(JAVACONSTS) $(COMMONDRBDOPTS) $(JAVAPROPERTYRULES)

golang: $(GOCONSTS)

cleancommon:
	rm -f $(COMMONDRBDOPTS)

cleanpythonproto:
	rm -f $(PYS)

cleanpython: cleancommon
	rm -f $(PYCONSTS) $(PYPROPS)

cleanjava: cleancommon
	rm -f $(JAVAS) $(JAVACONSTS)
	rm -Rf $(JAVABASEOUT)

clean: cleanpython cleanjava
