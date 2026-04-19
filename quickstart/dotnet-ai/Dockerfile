# Build and run the application
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/AiApi/AiApi.csproj", "src/AiApi/"]
RUN dotnet restore "src/AiApi/AiApi.csproj"
COPY . .
WORKDIR "/src/src/AiApi"
RUN dotnet build "AiApi.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AiApi.csproj" -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AiApi.dll"]
