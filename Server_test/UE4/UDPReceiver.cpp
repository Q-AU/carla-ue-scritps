// Fill out your copyright notice in the Description page of Project Settings.


#include "UDPReceiver.h"
#include "..\Public\UDPReceiver.h"

// Sets default values
AUDPReceiver::AUDPReceiver()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void AUDPReceiver::BeginPlay()
{
	Super::BeginPlay();
	StartUDPReceiver();

	
}
void AUDPReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Super::EndPlay(EndPlayReason);
	//~~~~~~~~~~~~~~~~

	delete UDPReceiver;
	UDPReceiver = nullptr;

	//Clear all sockets!
	//		makes sure repeat plays in Editor dont hold on to old sockets!
	if (ListenSocket)
	{
		ListenSocket->Close();
		ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(ListenSocket);
	}
}

void AUDPReceiver::Recv(const FArrayReaderPtr& ArrayReaderPtr, const FIPv4Endpoint& EndPt)
{
	GEngine->AddOnScreenDebugMessage(-1, 1.0f, FColor::Yellow, FString::Printf(TEXT("Bytes received: "), ArrayReaderPtr->Num()));
}

void AUDPReceiver::StartUDPReceiver()
{

	FIPv4Address Addr;
	FIPv4Address::Parse(TEXT("0.0.0.0"), Addr);


	FIPv4Address Group;
	FIPv4Address::Parse(TEXT("224.1.1.1"), Group);

	//Create Socket
	FIPv4Endpoint Endpoint(Addr, 6000);
	FIPv4Endpoint AnyEndpoint(FIPv4Address::Any, 6000);

	//BUFFER SIZE
	int32 BufferSize = 2 * 1024 * 1024;

	ListenSocket = FUdpSocketBuilder("MySocket")
		.WithMulticastLoopback()
		.WithMulticastTtl(2)
		.WithBroadcast()
		.JoinedToGroup(Group)
		.AsNonBlocking()
		.AsReusable()
		.BoundToEndpoint(AnyEndpoint)
		.BoundToAddress(Addr)
		.BoundToPort(6000)
		.WithReceiveBufferSize(BufferSize)
		.Build();

	FTimespan ThreadWaitTime = FTimespan::FromMilliseconds(100);
	UDPReceiver = new FUdpSocketReceiver(ListenSocket, ThreadWaitTime, TEXT("MyThread"));

	UDPReceiver->OnDataReceived().BindUObject(this, &AUDPReceiver::Recv);
	//OnReceiveSocketStartedListening.Broadcast();

	UDPReceiver->Start();
}

// Called every frame
void AUDPReceiver::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

