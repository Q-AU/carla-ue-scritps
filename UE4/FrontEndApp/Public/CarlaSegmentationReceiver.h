// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

#include "Components/StaticMeshComponent.h"
#include "Runtime/Sockets/Public/Sockets.h"
#include "Runtime/Sockets/Public/SocketSubsystem.h"
#include "Runtime/Networking/Public/Interfaces/IPv4/IPv4Address.h"
#include <vector>
#include "Runtime/Engine/Public/ImageUtils.h"
#include "../CarlaStreamingCommon.h"

#include "CarlaSegmentationReceiver.generated.h"

UCLASS()
class FRONTENDAPP_API ACarlaSegmentationReceiver : public AActor
{
	GENERATED_BODY()

private:
	TCPSocketListener* listener;
	TCPImageReceiver* imageReceiver;
public:	
	// Sets default values for this actor's properties
	ACarlaSegmentationReceiver();
	virtual void BeginDestroy();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	uint8* lastReceivedImage;

	UPROPERTY(BlueprintReadWrite, VisibleAnywhere)
		UStaticMeshComponent* Plane;
	UPROPERTY(BlueprintReadWrite, VisibleAnywhere)
		UTexture2D* camTexture;
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
		int receivePort = 2338;

	// Called every frame
	virtual void Tick(float DeltaTime) override;

};