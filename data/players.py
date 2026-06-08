# Curated list of forwards / attacking players for the Golden Boot selector.
# Organised by team — realistic goal-scorers, not full squads.

GOLDEN_BOOT_PLAYERS: dict[str, list[str]] = {
    # Group A
    "Mexico": ["Santiago Giménez", "Raúl Jiménez", "Julián Quiñones", "Alexis Vega"],
    "South Korea": ["Son Heung-Min", "Oh Hyeon-gyu", "Cho Gue-Sung"],
    "South Africa": ["Percy Tau", "Lyle Foster", "Evidence Makgopa"],
    "Czechia": ["Patrik Schick", "Tomáš Čvančara", "Adam Hložek"],
    # Group B
    "Canada": ["Jonathan David", "Cyle Larin", "Tajon Buchanan", "Alphonso Davies"],
    "Switzerland": ["Breel Embolo", "Zeki Amdouni", "Noah Okafor"],
    "Qatar": ["Akram Afif", "Almoez Ali"],
    "Bosnia-Herzegovina": ["Edin Džeko", "Ermedin Demirović", "Armin Hodžić"],
    # Group C
    "Brazil": ["Vinícius Jr.", "Rodrygo", "Endrick", "Raphinha", "Gabriel Martinelli", "Matheus Cunha"],
    "Morocco": ["Youssef En-Nesyri", "Hakim Ziyech", "Soufiane Rahimi", "Ayoub El Kaabi"],
    "Haiti": ["Frantzdy Pierrot", "Duckens Nazon"],
    "Scotland": ["Che Adams", "Lawrence Shankland", "Scott McTominay"],
    # Group D
    "United States": ["Christian Pulisic", "Ricardo Pepi", "Folarin Balogun", "Brendan Aaronson"],
    "Paraguay": ["Miguel Almirón", "Antonio Sanabria", "Julio Enciso"],
    "Australia": ["Mitchell Duke", "Martin Boyle", "Nestory Irankunda"],
    "Türkiye": ["Kerem Aktürkoğlu", "Cenk Tosun", "Baris Yilmaz"],
    # Group E
    "Germany": ["Kai Havertz", "Florian Wirtz", "Leroy Sané", "Niclas Füllkrug", "Jamal Musiala"],
    "Curaçao": ["Cuco Martina", "Leandro Bacuna"],
    "Ivory Coast": ["Sébastien Haller", "Nicolas Pépé", "Simon Adingra", "Wilfried Zaha"],
    "Ecuador": ["Enner Valencia", "Gonzalo Plata", "Jeremy Sarmiento"],
    # Group F
    "Netherlands": ["Cody Gakpo", "Wout Weghorst", "Donyell Malen", "Xavi Simons"],
    "Japan": ["Takumi Minamino", "Ritsu Doan", "Ao Tanaka", "Kaoru Mitoma"],
    "Sweden": ["Viktor Gyökeres", "Dejan Kulusevski", "Alexander Isak"],
    "Tunisia": ["Issam Jebali", "Sayfallah Ltaief", "Seifeddine Jaziri"],
    # Group G
    "Belgium": ["Romelu Lukaku", "Leandro Trossard", "Jeremy Doku", "Loïs Openda"],
    "Egypt": ["Mohamed Salah", "Omar Marmoush", "Mostafa Mohamed"],
    "Iran": ["Mehdi Taremi", "Sardar Azmoun", "Ali Gholizadeh"],
    "New Zealand": ["Chris Wood", "Oli Sail", "Matthew Garbett"],
    # Group H
    "Spain": ["Mikel Oyarzabal", "Dani Olmo", "Nico Williams", "Pedri", "Yeremy Pino"],
    "Cape Verde": ["Garry Rodrigues", "Ryan Mendes"],
    "Saudi Arabia": ["Salem Al-Dawsari", "Firas Al-Buraikan", "Mohammed Al-Buraik"],
    "Uruguay": ["Darwin Núñez", "Facundo Torres", "Matías Vecino", "Federico Valverde"],
    # Group I
    "France": ["Kylian Mbappé", "Marcus Thuram", "Ousmane Dembélé", "Michael Olise", "Bradley Barcola", "Randal Kolo Muani"],
    "Senegal": ["Sadio Mané", "Ismaïla Sarr", "Nicolas Jackson", "Habib Diallo"],
    "Iraq": ["Amjed Attwan", "Ali Adnan", "Mohanad Ali"],
    "Norway": ["Erling Haaland", "Alexander Sørloth", "Ola Solbakken"],
    # Group J
    "Argentina": ["Lionel Messi", "Julián Álvarez", "Lautaro Martínez", "Ángel Di María"],
    "Algeria": ["Islam Slimani", "Youcef Atal", "Andy Delort"],
    "Austria": ["Marcel Sabitzer", "Marko Arnautović", "Christoph Baumgartner"],
    "Jordan": ["Yazan Al-Naimat", "Musa Al-Taamari", "Ahmad Hayel"],
    # Group K
    "Portugal": ["Cristiano Ronaldo", "Rafael Leão", "João Félix", "Gonçalo Ramos", "Diogo Jota"],
    "Congo DR": ["Yannick Bolasie", "Cédric Bakambu", "Jonathan Bolingi"],
    "Uzbekistan": ["Eldor Shomurodov", "Otabek Shukurov"],
    "Colombia": ["Luis Díaz", "Jhon Córdoba", "Radamel Falcao", "Cucho Hernández"],
    # Group L
    "England": ["Harry Kane", "Bukayo Saka", "Phil Foden", "Cole Palmer", "Marcus Rashford", "Ollie Watkins"],
    "Croatia": ["Andrej Kramarić", "Ivan Perišić", "Bruno Petković"],
    "Ghana": ["Jordan Ayew", "Antoine Semenyo", "Iñaki Williams", "Osman Bukari"],
    "Panama": ["Rolando Blackburn", "Ismael Díaz", "Cecilio Waterman"],
}


def get_all_players() -> list[str]:
    """Returns a sorted flat list of all players, prefixed with their team."""
    players = []
    for team, squad in GOLDEN_BOOT_PLAYERS.items():
        for player in squad:
            players.append(f"{player} ({team})")
    return sorted(players, key=lambda x: x.split("(")[0].strip())
