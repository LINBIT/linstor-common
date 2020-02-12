PYTHON ?= python3
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
	$(PYTHON) ./genconsts.py python ../linstor

$(JAVAPROPOUT):
	mkdir -p $@

$(JAVAPROPERTYRULES): genproperties.py $(COMMONPROPERTIES) $(COMMONDRBDOPTS) $(JAVAPROPOUT)
	$(PYTHON) ./genproperties.py java $(COMMONPROPERTIES) $(COMMONDRBDOPTS) > $@

$(PYPROPS): genproperties.py $(COMMONPROPERTIES) $(COMMONDRBDOPTS)
	$(PYTHON) ./genproperties.py python $(COMMONPROPERTIES) $(COMMONDRBDOPTS) > $@

$(COMMONDRBDOPTS): gendrbdoptions.py
	$(PYTHON) ./gendrbdoptions.py $(COMMONDRBDOPTS)

$(JAVAAPIOUT):
	mkdir -p $@

$(JAVACONSTS): genconsts.py consts.json $(JAVAAPIOUT)
	$(PYTHON) ./genconsts.py java $(JAVAAPIOUT)

$(GOCONSTS): genconsts.py consts.json
	$(PYTHON) ./genconsts.py golang ../

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
