COMMONSRC=$(wildcard proto/*.proto)
JAVASRC=$(wildcard proto/javainternal/*.proto)
COMMONNOEND=$(COMMONSRC:.proto=)
JAVANOEND=$(COMMONNOEND) $(JAVASRC:.proto=)

PYOUT=../
PYSUFF=_pb2.py
PYS=$(patsubst %,$(PYOUT)/%$(PYSUFF),$(COMMONNOEND))
PYCONSTS=../linstor/sharedconsts.py
PYPROPS=../linstor/properties.py

JAVAOUT=../src/com/linbit/linstor
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

$(PYPROPS): properties.json
	./genproperties.py properties.json python > $@

$(JAVACONSTS): consts.json
	./genconsts.py java > $@

python: $(PYS) $(PYCONSTS) $(PYPROPS)

java: $(JAVAS) $(JAVACONSTS)

cleanpython:
	rm -f $(PYS) $(PYCONSTS)

cleanjava:
	rm -f $(JAVAS) $(JAVACONSTS)

clean: cleanpython cleanjava
