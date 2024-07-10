import matplotlib.pyplot as plt
import numpy as np
import os



def print_img(imagem):
    
    plt.imshow(imagem, cmap='jet')
    plt.show()

def to_array(directory, target):
    arquivos = os.listdir(directory)

    imagens = []

    for arquivo in arquivos:
        path = os.path.join(directory, arquivo)
        imagem = np.loadtxt(path)
        imagens.append(imagem)

    imagens = np.array(imagens)

    targets = np.array([target]*imagens.shape[0])

    np.save(f'imagens_{target}.npy', imagens)

    return imagens, targets


if __name__ == '__main__':

    """
    directory = input('Forneca o caminho para o diretório :')
    imagens, target = to_array(directory, "healthy")

    print(imagens.shape)
    print(target.shape)
    print(target)
    print_img(imagens[8])
    """
    imagens = np.load('imagens_healthy.npy')
    print(imagens.shape)
    print_img(imagens[8])

    
