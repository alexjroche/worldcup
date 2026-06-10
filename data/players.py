# Curated list of forwards / attacking players for the Golden Boot selector.
# Organised by team — realistic goal-scorers, not full squads.

GOLDEN_BOOT_PLAYERS: dict[str, list[str]] = {
    # Group A
    "Mexico": ["Santiago Giménez", "Raúl Jiménez", "Julián Quiñones", "Alexis Vega", "Hirving Lozano"],
    "South Korea": ["Son Heung-Min", "Lee Kang-in", "Oh Hyeon-gyu", "Cho Gue-Sung"],
    "South Africa": ["Percy Tau", "Lyle Foster", "Evidence Makgopa", "Themba Zwane"],
    "Czechia": ["Patrik Schick", "Tomáš Čvančara", "Adam Hložek", "Lukáš Provod"],
    # Group B
    "Canada": ["Jonathan David", "Cyle Larin", "Tajon Buchanan", "Alphonso Davies"],
    "Switzerland": ["Breel Embolo", "Zeki Amdouni", "Noah Okafor", "Granit Xhaka", "Fabian Rieder"],
    "Qatar": ["Akram Afif", "Almoez Ali", "Hassan Al-Haydos"],
    "Bosnia-Herzegovina": ["Edin Džeko", "Ermedin Demirović", "Armin Hodžić"],
    # Group C
    "Brazil": ["Vinícius Jr.", "Rodrygo", "Endrick", "Raphinha", "Gabriel Martinelli", "Matheus Cunha", "Bruno Guimarães", "Lucas Paquetá"],
    "Morocco": ["Youssef En-Nesyri", "Hakim Ziyech", "Soufiane Rahimi", "Ayoub El Kaabi", "Achraf Hakimi", "Azzedine Ounahi"],
    "Haiti": ["Frantzdy Pierrot", "Duckens Nazon"],
    "Scotland": ["Che Adams", "Lawrence Shankland", "Scott McTominay", "Ryan Christie"],
    # Group D
    "United States": ["Christian Pulisic", "Ricardo Pepi", "Folarin Balogun", "Brendan Aaronson", "Gio Reyna", "Tim Weah"],
    "Paraguay": ["Miguel Almirón", "Antonio Sanabria", "Julio Enciso"],
    "Australia": ["Mitchell Duke", "Martin Boyle", "Nestory Irankunda", "Cameron Devlin"],
    "Türkiye": ["Kerem Aktürkoğlu", "Cenk Tosun", "Baris Yilmaz", "Hakan Çalhanoğlu", "Arda Güler"],
    # Group E
    "Germany": ["Kai Havertz", "Florian Wirtz", "Leroy Sané", "Niclas Füllkrug", "Jamal Musiala", "İlkay Gündoğan", "Joshua Kimmich", "Thomas Müller"],
    "Curaçao": ["Cuco Martina", "Leandro Bacuna"],
    "Ivory Coast": ["Sébastien Haller", "Nicolas Pépé", "Simon Adingra", "Wilfried Zaha", "Franck Kessié"],
    "Ecuador": ["Enner Valencia", "Gonzalo Plata", "Jeremy Sarmiento", "Moisés Caicedo"],
    # Group F
    "Netherlands": ["Cody Gakpo", "Wout Weghorst", "Donyell Malen", "Xavi Simons", "Memphis Depay", "Tijjani Reijnders", "Frenkie de Jong", "Steven Bergwijn"],
    "Japan": ["Takumi Minamino", "Ritsu Doan", "Ao Tanaka", "Kaoru Mitoma", "Takefusa Kubo", "Junya Ito"],
    "Sweden": ["Viktor Gyökeres", "Dejan Kulusevski", "Alexander Isak", "Emil Forsberg"],
    "Tunisia": ["Issam Jebali", "Sayfallah Ltaief", "Seifeddine Jaziri", "Youssef Msakni"],
    # Group G
    "Belgium": ["Romelu Lukaku", "Leandro Trossard", "Jeremy Doku", "Loïs Openda", "Kevin De Bruyne", "Axel Witsel", "Yannick Carrasco"],
    "Egypt": ["Mohamed Salah", "Omar Marmoush", "Mostafa Mohamed", "Trezeguet"],
    "Iran": ["Mehdi Taremi", "Sardar Azmoun", "Ali Gholizadeh", "Alireza Jahanbakhsh"],
    "New Zealand": ["Chris Wood", "Oli Sail", "Matthew Garbett"],
    # Group H
    "Spain": ["Mikel Oyarzabal", "Dani Olmo", "Nico Williams", "Pedri", "Lamine Yamal", "Álvaro Morata", "Rodri", "Gavi", "Fabián Ruiz", "Yeremy Pino"],
    "Cape Verde": ["Garry Rodrigues", "Ryan Mendes", "Júlio Tavares"],
    "Saudi Arabia": ["Salem Al-Dawsari", "Firas Al-Buraikan", "Mohammed Al-Buraik", "Sami Al-Najei"],
    "Uruguay": ["Darwin Núñez", "Facundo Torres", "Federico Valverde", "Rodrigo Bentancur", "Ronald Araújo"],
    # Group I
    "France": ["Kylian Mbappé", "Marcus Thuram", "Ousmane Dembélé", "Michael Olise", "Bradley Barcola", "Randal Kolo Muani", "Antoine Griezmann", "Aurélien Tchouaméni", "Adrien Rabiot", "Kingsley Coman"],
    "Senegal": ["Sadio Mané", "Ismaïla Sarr", "Nicolas Jackson", "Habib Diallo", "Iliman Ndiaye"],
    "Iraq": ["Amjed Attwan", "Ali Adnan", "Mohanad Ali"],
    "Norway": ["Erling Haaland", "Alexander Sørloth", "Ola Solbakken", "Martin Ødegaard"],
    # Group J
    "Argentina": ["Lionel Messi", "Julián Álvarez", "Lautaro Martínez", "Ángel Di María", "Alexis Mac Allister", "Rodrigo De Paul", "Enzo Fernández", "Paulo Dybala"],
    "Algeria": ["Islam Slimani", "Youcef Atal", "Andy Delort", "Riyad Mahrez"],
    "Austria": ["Marcel Sabitzer", "Marko Arnautović", "Christoph Baumgartner", "Florian Grillitsch"],
    "Jordan": ["Yazan Al-Naimat", "Musa Al-Taamari", "Ahmad Hayel"],
    # Group K
    "Portugal": ["Cristiano Ronaldo", "Rafael Leão", "João Félix", "Gonçalo Ramos", "Diogo Jota", "Bruno Fernandes", "Bernardo Silva", "Vitinha", "Pedro Neto"],
    "Congo DR": ["Yannick Bolasie", "Cédric Bakambu", "Jonathan Bolingi"],
    "Uzbekistan": ["Eldor Shomurodov", "Otabek Shukurov", "Jaloliddin Masharipov"],
    "Colombia": ["Luis Díaz", "Jhon Córdoba", "Radamel Falcao", "Cucho Hernández", "James Rodríguez", "Juan Cuadrado"],
    # Group L
    "England": ["Harry Kane", "Bukayo Saka", "Phil Foden", "Cole Palmer", "Marcus Rashford", "Ollie Watkins", "Jude Bellingham", "Declan Rice", "Trent Alexander-Arnold", "Jack Grealish"],
    "Croatia": ["Andrej Kramarić", "Ivan Perišić", "Bruno Petković", "Luka Modrić", "Mateo Kovačić"],
    "Ghana": ["Jordan Ayew", "Antoine Semenyo", "Iñaki Williams", "Osman Bukari", "Mohammed Kudus"],
    "Panama": ["Rolando Blackburn", "Ismael Díaz", "Cecilio Waterman"],
}


def get_all_players() -> list[str]:
    """Returns a sorted flat list of all players, prefixed with their team."""
    players = []
    for team, squad in GOLDEN_BOOT_PLAYERS.items():
        for player in squad:
            players.append(f"{player} ({team})")
    return sorted(players, key=lambda x: x.split("(")[0].strip())


# Curated list of goalkeepers for the Golden Glove selector.
GOLDEN_GLOVE_KEEPERS: dict[str, list[str]] = {
    # Group A
    "Mexico": ["Luis Malagón", "Guillermo Ochoa"],
    "South Korea": ["Kim Seung-gyu", "Jo Hyeon-woo"],
    "South Africa": ["Ronwen Williams", "Veli Mothwa"],
    "Czechia": ["Jindřich Staněk", "Tomáš Vaclík"],
    # Group B
    "Canada": ["Milan Borjan", "Maxime Crépeau"],
    "Switzerland": ["Yann Sommer", "Gregor Kobel"],
    "Qatar": ["Meshaal Barsham"],
    "Bosnia-Herzegovina": ["Ibrahim Šehić", "Kenan Pirić"],
    # Group C
    "Brazil": ["Alisson", "Ederson"],
    "Morocco": ["Yassine Bounou", "Munir Mohamedi"],
    "Haiti": ["Josué Duverger"],
    "Scotland": ["Angus Gunn", "Craig Gordon"],
    # Group D
    "United States": ["Matt Turner", "Patrick Schulte"],
    "Paraguay": ["Antony Silva", "Gastón Olvedo"],
    "Australia": ["Mat Ryan", "Joe Gauci"],
    "Türkiye": ["Mert Günok", "Altay Bayındır"],
    # Group E
    "Germany": ["Manuel Neuer", "Marc-André ter Stegen"],
    "Curaçao": ["Eloy Room"],
    "Ivory Coast": ["Yahia Fofana", "Ali Badra Sangaré"],
    "Ecuador": ["Hernán Galíndez", "Alexander Domínguez"],
    # Group F
    "Netherlands": ["Bart Verbruggen", "Mark Flekken"],
    "Japan": ["Shuichi Gonda", "Zion Suzuki"],
    "Sweden": ["Robin Olsen", "Samuel Brolin"],
    "Tunisia": ["Aymen Dahmen", "Mouez Hassen"],
    # Group G
    "Belgium": ["Koen Casteels", "Thomas Kaminski"],
    "Egypt": ["Mohamed El-Shenawy", "Ahmed El-Shenawy"],
    "Iran": ["Alireza Beiranvand", "Hossein Hosseini"],
    "New Zealand": ["Oli Sail", "Stefan Marinovic"],
    # Group H
    "Spain": ["Unai Simón", "David Raya", "Álex Remiro"],
    "Cape Verde": ["Vozinha", "Patrick Mendes"],
    "Saudi Arabia": ["Mohammed Al-Owais", "Nawaf Al-Aqidi"],
    "Uruguay": ["Sergio Rochet", "Gilbert Álvarez"],
    # Group I
    "France": ["Mike Maignan", "Alphonse Areola"],
    "Senegal": ["Edouard Mendy", "Seny Dieng"],
    "Iraq": ["Jalal Hassan", "Mohammed Hameed"],
    "Norway": ["Ørjan Nyland", "Rune Jarstein"],
    # Group J
    "Argentina": ["Emiliano Martínez", "Geronimo Rulli"],
    "Algeria": ["Rais M'Bolhi", "Alexandre Oukidja"],
    "Austria": ["Patrick Pentz", "Alexander Schlager"],
    "Jordan": ["Yazeed Abulaila", "Ibrahim Shelbaieh"],
    # Group K
    "Portugal": ["Diogo Costa", "Rui Patrício"],
    "Congo DR": ["Lionel Mpasi"],
    "Uzbekistan": ["Utkir Yusupov", "Eldorbek Suyunov"],
    "Colombia": ["Camilo Vargas", "David Ospina"],
    # Group L
    "England": ["Jordan Pickford", "Nick Pope", "Aaron Ramsdale"],
    "Croatia": ["Dominik Livaković", "Ivica Ivušić"],
    "Ghana": ["Lawrence Ati-Zigi", "Joe Wollacott"],
    "Panama": ["Luis Mejía", "Orlando Mosquera"],
}


def get_goalkeepers() -> list[str]:
    """Returns a sorted flat list of goalkeepers, prefixed with their team."""
    keepers = []
    for team, squad in GOLDEN_GLOVE_KEEPERS.items():
        for keeper in squad:
            keepers.append(f"{keeper} ({team})")
    return sorted(keepers, key=lambda x: x.split("(")[0].strip())
