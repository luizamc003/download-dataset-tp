import matplotlib.pyplot as plt
import numpy as np
import re
import os

def print_img(imagem):
    
    plt.imshow(imagem, cmap='jet')
    plt.show()

def to_array(directory, target):
    arquivos = os.listdir(directory)

    imagens = []
    
    for arquivo in arquivos:
        path = os.path.join(directory, arquivo)
        try:
            with open(path, 'r') as file:
                primeira_linha = file.readline()
                if ";" in primeira_linha:
                    delimitador = ";"
                else:
                    delimitador = " "

            imagem = np.loadtxt(path, delimiter=delimitador)

        except ValueError as e:
            print(e)
            print(arquivo)
            continue
        
        imagens.append(imagem)

    imagens = np.array(imagens)

    targets = np.array([target]*imagens.shape[0])

    #np.save(f'imagens_{target}.npy', imagens)

    return imagens, targets


if __name__ == '__main__':

    imagens, target = to_array("dataset\\sick", "sick")

    print(imagens.shape)
    print(target.shape)
    print_img(imagens[8])
    print_img(imagens[257])
    """
    imagens = np.load('imagens_healthy.npy')
    print(imagens.shape)
    print_img(imagens[8])
    """