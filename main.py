import numpy as np
import math
from cmath import sqrt

ERR = 1e-4

SUPPORTED_FORMATS = [np.float32, np.float64, np.float_, np.complex64, np.complex128, np.complex_]

def calc_c (a,b):
    """
    Calcula o parâmetro c, definido na página 3 do enunciado 
        :param a: w[i,k] - elemento da matriz W na posição (i, k)
        :param b: w[j,k] - elemento da matriz W na posição (j, k)
    """
    if a.dtype not in SUPPORTED_FORMATS:
        raise TypeError("Matriz de formato não suportado: {}! \
            \nNote que variáveis inteiras acarretam em perdas severas por arredondamento."
            .format(a.dtype))

    if b.dtype not in SUPPORTED_FORMATS:
        raise TypeError("Matriz de formato não suportado: {}! \
            \nNote que variáveis inteiras acarretam em perdas severas por arredondamento."
            .format(b.dtype))

    if abs(a) > abs(b):
        T = -np.divide(b,a)
        cos = 1/np.sqrt(1+(T**2))
    else :
        T = -np.divide(a,b)
        cos = calc_s(a,b)*T
    return cos

def calc_s (a,b):
    """
    Calcula o parâmetro s, definido na página 3 do enunciado 
        :param a: w[i,k] - elemento da matriz W na posição (i, k)
        :param b: w[j,k] - elemento da matriz W na posição (j, k)
    """
    if a.dtype not in SUPPORTED_FORMATS:
        raise TypeError("Matriz de formato não suportado: {}! \
            \nNote que variáveis inteiras acarretam em perdas severas por arredondamento."
            .format(a.dtype))

    if b.dtype not in SUPPORTED_FORMATS:
        raise TypeError("Matriz de formato não suportado: {}! \
            \nNote que variáveis inteiras acarretam em perdas severas por arredondamento."
            .format(b.dtype))
        
    if abs(a) > abs(b):
        T = -np.divide(b,a)
        sen = calc_c(a,b)*T
    else :
        T = -np.divide(a,b) 
        sen = 1/np.sqrt(1+(T**2))
    return sen

def rot_givens(W,n,m,i,j,c,s):
    """
    Implementa Rotação de Givens para matriz W
        :param W: ndarray
        :param i: linha a ser rotacionada
        :param j: linha a ser zerada
        :param c: 
        :param s: 
    """
    if W.dtype not in SUPPORTED_FORMATS:
        raise TypeError("Matriz de formato não suportado: {}! \
            \nNote que variáveis inteiras acarretam em perdas severas por arredondamento."
            .format(W.dtype))
    col = 0
    while (W[i][col] == 0 and W[j][col] == 0):
        col += 1

    for r in range(col,m):
        aux = c*W[i][r] - s*W[j][r]
        W[j][r] = s*W[i][r] + c*W[j][r]
        W[i][r] = aux

def zera_elemento(W,Wc,i,j,k):
    """
    Realiza uma rotação de Givens de modo a zerar o elemento (j,k)
        :param W: ndarray
        :param Wc: array que define seno e cosseno
        :param i: linha a ser rotacionada
        :param j: linha a ser zerada
        :param k: coluna a ser zerada
    """
    if W.dtype not in SUPPORTED_FORMATS:
        raise TypeError("Matriz de formato não suportado: {}! \
            \nNote que variáveis inteiras acarretam em perdas severas por arredondamento."
            .format(W.dtype))
    n, m = W.shape
    _s = calc_s(Wc[i,k], Wc[j,k])
    _c = calc_c(Wc[i,k], Wc[j,k])
    return rot_givens(W, n, m, i, j, _c, _s)

def fatorar_qr (W):
    """
    Aplica a fatoração QR para matriz W
        :param W: ndarray
    """
    if W.dtype not in SUPPORTED_FORMATS:
        raise TypeError("Matriz de formato não suportado: {}! \
            \nNote que variáveis inteiras acarretam em perdas severas por arredondamento."
            .format(W.dtype))

    n, m = W.shape

    for k in range(m):
        for j in range(n-1,k,-1):
            i = j-1
            if W[j][k] != 0 :
               #zera_elemento(W,W,i,j,k)
               _s = calc_s(W[i][k], W[j][k])
               _c = calc_c(W[i][k], W[j][k])
               rot_givens(W,n,m,i,j,_c,_s)
               


def resolver_sist(W, A):
    """
    Dadas matrizes W e A, encontra a matriz H, tal que
         W*H = A
    Função Principal da Primeira Tarefa c) d)
        :param W: ndarray n;p
        :param A: ndarray n;m
    """
    n1, p = W.shape
    n2, m = A.shape
    n = None

    if n1 != n2:
        raise ValueError("Matrizes de tamanhos incompatíveis!")
    else:
        n = n1

    H = np.zeros((p, m))

    for k in range(p):
        intervalo = range(k, n)
        for j in intervalo[::-1]:
            i = j-1
            if W[j][k] != 0 :
                # n, m = W.shape
                _s = calc_s(W[i,k], W[j,k])
                _c = calc_c(W[i,k], W[j,k])
                rot_givens(W,n,p,i,j,_c,_s)
                rot_givens(A,n,m,i,j,_c,_s)

    intervalo = [i for i in range(p)]
    for k in intervalo[::-1]:
        soma = np.array(1).astype(np.double)
        for i in range(k,p-1):
            soma = soma + W[k][i]*H[i][j]
        for j in range(m):
            H[k][j] = (A[k][j] - soma)/W[k][k]

    return H

    
def residuo(A,W,H):
    """
    Calculo residuo para (A-WH)
        :param W: ndarray n;m
        :param A: ndarray n;p
        :param W: ndarray p;m
    """
    na,ma = A.shape
    nw,pw = W.shape
    ph,mh = H.shape

    if na != nw or ma != mh or ph != pw :
        raise ValueError("Matrizes não compatíveis")
    else:
        n = na
        m = mh
        p = ph

    WH = np.dot(W,H)
    # erro = 0.0
    # for i in range(n):
    #     for j in range(m):
    #         if (A[i][j] - WH[i][j]) > ERR:
    #             erro = erro + (A[i][j] - WH[i][j])**2

    err = A - WH
    erro = np.sum(np.dot(err, err))
    return erro

    
def normaliza(M):
    """
    Normaliza a matriz M
        :param M: 
    """
    soma_colunas = np.sum(M, axis=0)
    print(soma_colunas)
    n, m = M.shape
    for i in range(n):
        for j in range(m):
            M[i][j] = np.divide(M[i][j], soma_colunas[j])

def calc_transpose(M):
    """
    Calcula a transposta da matriz M
        :param M: 
    """
    n, m = M.shape
    M_t = np.empty((m, n))
    for i in range(n):
        for j in range(m):
            M_t[j][i] = M[i][j]
    return M_t

def resolve_mmq(A, W, H, err):

    """
    Resolve o  MMQ 
    Função Principal da Segunda Tarefa
        :param A:
        :param W:
        :param H:
        :param err:
    """

    n, m = A.shape
    p, n = H.shape

    _A = A.copy()
    # W = np.random.rand(n, p)
    # W = np.ones((n, p))

    print()


    while residuo(A, W, H) > err:

        normaliza(W)
        _W = W.copy()

        H = resolver_sist(_W, A)
        # H[ H < 0 ] = 0

        print("H:")
        print(H)

        A = _A.copy()
        # A_t = calc_transpose(A)
        # H_t = calc_transpose(H)

        A_t = A.transpose()
        H_t = H.transpose()

        _W_t = resolver_sist(H_t, A_t)
        
        print("W_t:")
        print(W_t)

        # W = calc_transpose(W_t)
        _W = W_t.transpose()

        _W[ _W < 0 ] = 0

    return H

if __name__ == "__main__":

    '''
    Matriz W do enunciado
    '''
    np.set_printoptions(precision=3, suppress=True)

    W = np.array([[ 2,  1,  1, -1,  1],
                   [ 0,  3,  0,  1,  2],
                   [ 0,  0,  2,  2, -1],
                   [ 0,  0, -1,  1,  2],
                   [ 0,  0,  0,  3,  1.0]])

    zera_elemento(W,W, 2, 3, 2)
    print(W*np.sqrt(5))
    print(W)

    '''
    Verificar se é triangular
    '''
    
    fatorar_qr(W)
    print(W)
    for i in range(5):
        for j in range(5):
            if i > j :
                print(W[i][j])
    #print(W)
    
    
    '''
    Matriz b qualquer
    '''
    
    # b = np.array([[1],[1],[1],[1],[1]]).astype(np.double)
    # print(b)
    # zera_elemento(b,W,2,3,0)
    # print(b)
    

    


    