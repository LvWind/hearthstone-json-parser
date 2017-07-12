from urllib.request import urlopen, Request
import json
import csv
import sqlite3

def main():
    cards_data = download_card_json()
    
    save_json_to_file(cards_data)
    
    cards = json.loads(cards_data)
    
    save_cards_to_flat_csv(cards)
    save_cards_to_nested_csvs(cards)
    save_cards_to_database(cards)

def download_card_json():
    req = Request('https://api.hearthstonejson.com/v1/20022/enUS/cards.json', headers={'User-Agent' : "Magic Browser"}) 
    response = urlopen(req)
    responseStr = response.read().decode('utf-8')
    return responseStr

def save_json_to_file(json_text):
    text_file = open('output/cards.json', 'w')
    text_file.write(json_text)
    text_file.close()

def save_cards_to_flat_csv(cards):
    with open('output/cards_flat.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            'id',
            'player_class',
            'type',
            'name',
            'set',
            'text',
            'cost',
            'attack',
            'health',
            'rarity',
            'collectible',
            'flavor',
            'mechanics',
            'dust',
            'play_requirements',
            'race',
            'how_to_earn',
            'how_to_earn_golden',
            'targeting_arrow_text',
            'faction',
            'durability',
            'entourage'
        ])
        
        for card in cards:
            csvwriter.writerow([
                card.get('id'),
                card.get('playerClass'),
                card.get('type'),
                card.get('name'),
                card.get('set'),
                card.get('text'),
                card.get('cost'),
                card.get('attack'), 
                card.get('health'), 
                card.get('rarity'),
                card.get('collectible'),
                card.get('flavor'),
                card.get('mechanics'),
                card.get('dust'),
                card.get('playRequirements'),
                card.get('race'),
                card.get('howToEarn'),
                card.get('howToEarnGolden'), 
                card.get('targetingArrowText'),
                card.get('faction'),
                card.get('durability'),
                card.get('entourage')
            ])

def save_cards_to_nested_csvs(cards):
    with open('output/cards.csv', 'w', newline='') as cards_file:
        with open('output/mechanics.csv', 'w', newline='') as mechanics_file:
            with open('output/dust_costs.csv', 'w', newline='') as dust_file:
                with open('output/play_requirements.csv', 'w', newline='') as play_reqs_file:
                    with open('output/entourages.csv', 'w', newline='') as entourage_file:
                        cards_writer = csv.writer(cards_file)
                        mechanics_writer = csv.writer(mechanics_file)
                        dust_writer = csv.writer(dust_file)
                        play_reqs_writer = csv.writer(play_reqs_file)
                        entourage_writer = csv.writer(entourage_file)

                        cards_writer.writerow([
                            'card_id',
                            'playerClass',
                            'type',
                            'name',
                            'set',
                            'text',
                            'cost',
                            'attack',
                            'health',
                            'rarity',
                            'collectible',
                            'flavor',
                            'race',
                            'how_to_earn',
                            'how_to_earn_golden',
                            'targeting_arrow_text',
                            'faction',
                            'durability'
                        ])

                        mechanics_writer.writerow(["card_id", "mechanic"])
                        dust_writer.writerow(["card_id", "action", "cost"])
                        play_reqs_writer.writerow(["card_id", "play_requirement", "value"])
                        entourage_writer.writerow(["card_id", "entourage_card_id"])

                        for card in cards:
                            cards_writer.writerow([
                                card.get('id'),
                                card.get('playerClass'),
                                card.get('type'),
                                card.get('name'),
                                card.get('set'),
                                card.get('text'),
                                card.get('cost'),
                                card.get('attack'), 
                                card.get('health'), 
                                card.get('rarity'),
                                card.get('collectible'),
                                card.get('flavor'),
                                card.get('race'),
                                card.get('howToEarn'),
                                card.get('howToEarnGolden'), 
                                card.get('targetingArrowText'),
                                card.get('faction'),
                                card.get('durability')
                            ])

                            if (card.get("mechanics") != None):
                                for i in card["mechanics"]:
                                    mechanics_writer.writerow([card["id"], i])
    
                            if (card.get("dust") != None):
                                dust_writer.writerow([card["id"], "CRAFTING_NORMAL", card["dust"][0]])
                                dust_writer.writerow([card["id"], "CRAFTING_GOLDEN", card["dust"][1]])
                                dust_writer.writerow([card["id"], "DISENCHANT_NORMAL", card["dust"][2]])
                                dust_writer.writerow([card["id"], "DISENCHANT_GOLDEN", card["dust"][3]])
    
                            if (card.get("playRequirements") != None):
                                for key, value in card["playRequirements"].items():
                                    play_reqs_writer.writerow([card["id"], key, value])
    
                            if (card.get("entourage") != None):
                                for i in card["entourage"]:
                                    entourage_writer.writerow([card["id"], i])

def save_cards_to_database(cards):
    with sqlite3.connect('output/database.sqlite', isolation_level=None) as sql:
        sql.execute("""PRAGMA writable_schema = 1;""")
        sql.execute("""DELETE FROM sqlite_master WHERE type IN ('table', 'index', 'trigger')""")
        sql.execute("""PRAGMA writable_schema = 0;""")
        sql.execute("""VACUUM;""")
        sql.execute("""PRAGMA foreign_keys = ON;""")

        sql.execute("""CREATE TABLE cards(
            card_id TEXT PRIMARY KEY,
            player_class TEXT,
            type TEXT,
            name TEXT,
            _set TEXT,
            text TEXT,
            cost INTEGER,
            attack INTEGER,
            health INTEGER,
            rarity TEXT,
            collectible INTEGER,
            flavor TEXT,
            race TEXT,
            how_to_earn TEXT,
            how_to_earn_golden TEXT,
            targeting_arrow_text TEXT,
            faction TEXT,
            durability INTEGER
        );""")

        sql.execute("""CREATE TABLE mechanics(
            card_id TEXT,
            mechanic TEXT,
            FOREIGN KEY(card_id) REFERENCES cards(card_id)
        );""")

        sql.execute("""CREATE TABLE dust_costs(
            card_id TEXT,
            action TEXT,
            cost INTEGER,
            FOREIGN KEY(card_id) REFERENCES cards(card_id)
        );""")

        sql.execute("""CREATE TABLE play_requirements(
            card_id TEXT,
            play_requirement TEXT,
            value INTEGER,
            FOREIGN KEY(card_id) REFERENCES cards(card_id)
        );""")

        sql.execute("""CREATE TABLE entourages(
            card_id TEXT,
            entourage_card_id TEXT,
            FOREIGN KEY(card_id) REFERENCES cards(card_id),
            FOREIGN KEY(entourage_card_id) REFERENCES cards(card_id)
        );""")
        
        for card in cards:
            sql.execute(
                "INSERT OR IGNORE INTO cards VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (
                    card.get('id'),
                    card.get('playerClass'),
                    card.get('type'),
                    card.get('name'),
                    card.get('set'),
                    card.get('text'),
                    card.get('cost'),
                    card.get('attack'), 
                    card.get('health'), 
                    card.get('rarity'),
                    card.get('collectible'),
                    card.get('flavor'),
                    card.get('race'),
                    card.get('howToEarn'),
                    card.get('howToEarnGolden'), 
                    card.get('targetingArrowText'),
                    card.get('faction'),
                    card.get('durability'),
                )
            )
                
            if (card.get("mechanics") != None):
                for i in card["mechanics"]:
                    sql.execute(
                        "INSERT OR IGNORE INTO mechanics VALUES(?, ?);",
                        (card["id"], i, )
                    )

            if (card.get("dust") != None):
                sql.execute(
                    "INSERT OR IGNORE INTO dust_costs VALUES(?, ?, ?);",
                    (card["id"], "CRAFTING_NORMAL", card["dust"][0], )
                )
                sql.execute(
                    "INSERT OR IGNORE INTO dust_costs VALUES(?, ?, ?);",
                    (card["id"], "CRAFTING_GOLDEN", card["dust"][1], )
                )
                sql.execute(
                    "INSERT OR IGNORE INTO dust_costs VALUES(?, ?, ?);",
                    (card["id"], "DISENCHANT_NORMAL", card["dust"][2], )
                )
                sql.execute(
                    "INSERT OR IGNORE INTO dust_costs VALUES(?, ?, ?);",
                    (card["id"], "DISENCHANT_GOLDEN", card["dust"][3], )
                )

            if (card.get("playRequirements") != None):
                for key, value in card["playRequirements"].items():
                    sql.execute(
                        "INSERT OR IGNORE INTO play_requirements VALUES(?, ?, ?);",
                        (card["id"], key, value, )
                    )

        # Have to loop again after populating all cards so that the entourage_card_id FK lookup doesn't fail
        for card in cards:
            if (card.get("entourage") != None):
                for i in card["entourage"]:
                    sql.execute(
                        "INSERT OR IGNORE INTO entourages VALUES(?, ?);",
                        (card["id"], i, )
                    )

main()
