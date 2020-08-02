from transmission_rpc import Client

c = Client(address="shchepkina60.duckdns.org", port=9091, username="kotuxa", password="Korokino2020")

item = 1

for torrent in c.get_torrents():
    print(torrent.name)
