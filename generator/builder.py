import os
from generator.uploader.blockchain_con import Minter
from generator.attributes.attribute_builder import AttributesBuilder
from generator.random_data import randomifyattributes
from generator.attributes.attributes import Attribute
from generator.image_gen import ImageGen
from generator.chicken_type import ChickenType
from generator.uploader.upload import Uploader
import json
import time
import optparse

from generator.utils import bool_from_input, read_hashes, remove_hash, save_hash


def both():
    # Pregunta para su vaina
    public = input("Que es tu llave publico: ")
    private = input("Que es tu private key: ")
    is_this_test_net = bool_from_input("Prueba? (y/n): ")
    amount = int(input("Cuanto quieres mint? "))

    # Abrimos el minter
    minter = Minter(public, private, is_this_test_net)
    start = time.time()

    pre = None

    # Loop con amount
    for x in range(amount):
        print(f"Generating --- {x + 1} de {amount}")
        # Buscamos el id del cock por smart contract
        cock_id = minter.most_recent()
        times_checked = 0
        while cock_id == pre:
            if times_checked > 5:
                print("Algo fue mallo con el smart contract!")
                exit()
            cock_id = minter.most_recent()
            times_checked += 1

        pre = cock_id
        print(f"ID de cock {cock_id}")
        gen = ImageGen(ChickenType.DETAILED_COCK, cock_id, randomifyattributes(Attribute.GEN_0))
        mck = gen.draw()

        uploader = Uploader(
            gen.chicken_type,
            mck,
            AttributesBuilder.pretty_attributes(gen.color_data, gen.attributes)
        )
        h = uploader.upload()
        # Chequeamos el upload no funciono
        if not h:
            # Di lo y termina!
            print(f"Una problema con {x + 1}. Terminando...")
            break
        # Guarda hash para futuro
        save_hash(h)
        # Verifica el mint del smart contract con el id y nombre!!!
        pos = bool_from_input(f"Hacemos un mint con {mck} quien tiene id de {cock_id} en el smart contract? (y/n) ")
        if pos:
            res = minter.mint(h)
            # Chequea si no funciono
            if not res:
                # Di al usario y termina!!
                print(f"No podiamos hacer mint con {h} con {x + 1}.\nTerminando...")
                break
        else:
            print("Ok... Terminando...")
            # Quita el hash
            uploader.unpin(h)
            remove_hash(h)
            break
    
    end = time.time()
    print(f"Tiempo tomado {int(end - start)} segundos")

def generator(amount, save):
    if save:
        print("Vamos a guardar!")
    attributes = []

    start = time.time()
    for x in range(amount):
        print(f"Generating --- {x + 1} de {amount}")
        # Abre el class de generation
        gen = ImageGen(ChickenType.DETAILED_COCK, x, randomifyattributes(Attribute.GEN_0))
        mck = gen.draw()
        
        attributes.append({mck:AttributesBuilder.pretty_attributes(gen.color_data, gen.attributes)})

        if save:
            # Uploaderlo
            uploader = Uploader(
                gen.chicken_type,
                mck,
                AttributesBuilder.pretty_attributes(gen.color_data, gen.attributes)
            )
            # Busca hash
            _hash = uploader.upload()
            # Chequea que hash es falso
            if not _hash:
                print(f"Una problema con {mck} borrando...")
                os.unlink(mck + ".png")
                continue
            # Guarda hash
            save_hash(_hash)
    # Busca cuando se termino
    end = time.time()
    with open("attributes.json", 'w') as file:
        json.dump(attributes, file)
    print(f"Tiempo tomado para {amount} fue {int(end - start)} segundos")


def minter():
    # Pregunta para su llave
    public = input("Que es tu llave publico: ")
    private = input("Que es tu private key: ")
    is_this_test_net = input("Prueba? (y/n): ")
    if is_this_test_net == "y" or is_this_test_net == "Y":
        is_this_test_net = True
    else:
        is_this_test_net = False
    # Crea el minter 
    minter = Minter(public, private, is_this_test_net)
    # Busca los hashes
    hashes = read_hashes()
    # Ahora pon lo en el smart contract
    for _hash in hashes:
        # Busca el current cada vez
        print(f"Currentamente {minter.most_recent()}")

        res = minter.mint(_hash)
        if not res:
            print(f"Suggestion de compiler!!! {_hash}")
            break
        else:
            print(f"Successo!! para hash {_hash}")
        print(f"Currentamente ahora es {minter.most_recent()}")


def main():
    parser = optparse.OptionParser('usage %prog -m' + 'Method')
    parser.add_option('-m', dest='method', type='string', help='specify the method to run.\nmint o generate')

    options, args = parser.parse_args()
    method = options.method

    if not method:
        print("No pasaste un method...")
        exit()
    
    if method.lower() == "generate":
        amount = input("Cuantos vamos a generar? ")
        save = bool_from_input("Vamos a guardar? ")
        generator(int(amount), save)
    elif method.lower() == "mint":
        minter()
    elif method.lower() == "upload":
        both()
    else:
        print(f"El metodo {method} no existe...")
        exit()

if __name__ == "__main__":
    main()