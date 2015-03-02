CC = g++
CFLAGS = -c -Wall

all: client

client: main.o socketHelper.o
	$(CC) main.o socketHelper.o -o client

main.o: main.cpp
	$(CC) $(CFLAGS) main.cpp

socketHelper.o: socketHelper.cpp
	$(CC) $(CFLAGS) socketHelper.cpp

clean:
	rm -rf *o client