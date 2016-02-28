
all: docker

docker: Spawn.jar spawn.sh
	docker build -t java_spawn .

Spawn.jar: Spawn.class Manifest
	jar cfm Spawn.jar Manifest  *.class

Spawn.class: Spawn.java
	javac Spawn.java

run: Spawn.class
	java -cp . Spawn

clean:
	rm -f Spawn.class MyT.class Spawn.jar

.PHONY: all docker clean run
