COMMONDRBDOPTS=drbdoptions.json
COMMONPROPERTIES=properties.json


PYCONSTS=../linstor/sharedconsts.py
PYPROPS=../linstor/properties.py

JAVABASEOUT=../server/generated-src
JAVAOUT=$(JAVABASEOUT)/com/linbit
JAVAAPIOUT=$(JAVAOUT)/linstor/api
JAVACONSTS=$(JAVAAPIOUT)/ApiConsts.java
JAVAPROPOUT=$(JAVAAPIOUT)/prop
JAVAPROPERTYRULES=$(JAVAPROPOUT)/GeneratedPropertyRules.java

GOCONSTS=../apiconsts.go

# make java the default one
all: java

%.json:
	;

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

python: $(PYCONSTS) $(PYPROPS)

java: $(JAVACONSTS) $(COMMONDRBDOPTS) $(JAVAPROPERTYRULES)

golang: $(GOCONSTS)

cleancommon:
	rm -f $(COMMONDRBDOPTS)

cleanpython: cleancommon
	rm -f $(PYCONSTS) $(PYPROPS)

cleanjava: cleancommon
	rm -f $(JAVACONSTS) $(JAVAPROPERTYRULES)
	rm -Rf $(JAVAAPIOUT) $(JAVAPROPOUT)

clean: cleanpython cleanjava
