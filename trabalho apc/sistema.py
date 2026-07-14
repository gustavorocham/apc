import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


df_moradores = None
fig, ax = plt.subplots(figsize=(6, 4))
canvas = None

def carregar_dados():
    
    try:
       
        colunas = ['localidade', 'idade_calculada', 'renda_ind', 'G05'] 
        df = pd.read_csv('dados/PDAD_2024-Moradores.csv', sep=';', encoding='latin-1', usecols=colunas)
        
        
        # Removendo 88888 (Não declarado) e 99999 (Não se aplica)
        df = df[~df['renda_ind'].isin([88888, 99999])]
        df = df[~df['G05'].isin([88888, 99999])]
        df = df[~df['idade_calculada'].isin([88888, 99999])]
        
        mapa_ra = {
	    5241: "Plano Piloto",
            5242: "Gama",
            5243: "Taguatinga",
            5244: "Brazlândia",
            5245: "Sobradinho",
            5246: "Planaltina",
            5247: "Paranoá",
            5248: "Núcleo Bandeirante",
            5249: "Ceilândia"
            
        }
        return df
    except FileNotFoundError:
       
        print("Aviso: CSV não encontrado. Usando dados fictícios para teste.")
        dados_teste = {
            'localidade': ['Plano Piloto', 'Ceilândia', 'Taguatinga', 'Plano Piloto', 'Ceilândia'] * 20,
            'idade_calculada': [25, 40, 35, 60, 22] * 20,
            'renda_ind': [5000, 1500, 3000, 8000, 1200] * 20,
            'G05': [1, 2, 1, 1, 2] * 20  # 1 = Tem plano, 2 = Não tem
        }
        return pd.DataFrame(dados_teste)

def calcular_estatisticas(df_filtrado):
    
    if df_filtrado.empty:
        return 0, 0, 0
    
    media_idade = df_filtrado['idade_calculada'].mean()
    mediana_renda = df_filtrado['renda_ind'].median()
    
    
    pct_plano = (df_filtrado['G05'] == 1).mean() * 100
    
    return media_idade, mediana_renda, pct_plano

def atualizar_interface(event=None):
    
    ra = combo_ra.get()
    
    if ra == "Todas as RAs":
        df_filtrado = df_moradores
    else:
        df_filtrado = df_moradores[df_moradores['localidade'] == ra]
        
    media_id, med_renda, pct_plano = calcular_estatisticas(df_filtrado)
    
    
    lbl_stats.config(text=f"Média de Idade: {media_id:.1f} anos\n"
                          f"Mediana da Renda: R$ {med_renda:.2f}\n"
                          f"Cobertura de Plano de Saúde: {pct_plano:.1f}%")
    
   
    ax.clear()
    df_plot = df_filtrado.copy()
    
    bins_renda = [0, 1500, 3000, 5000, float('inf')]
    labels_renda = ['Até 1.5k', '1.5k-3k', '3k-5k', 'Mais de 5k']
    df_plot['faixa_renda'] = pd.cut(df_plot['renda_ind'], bins=bins_renda, labels=labels_renda)
    
    
    total_por_faixa = df_plot.groupby('faixa_renda', observed=False).size()
    com_plano = df_plot[df_plot['G05'] == 1].groupby('faixa_renda', observed=False).size()
    cobertura = (com_plano / total_por_faixa) * 100
    
    cobertura.plot(kind='bar', ax=ax, color='#4C72B0', edgecolor='black')
    ax.set_title(f"Cobertura de Plano de Saúde por Renda\n({ra})")
    ax.set_ylabel("% com Plano de Saúde")
    ax.set_xlabel("Faixa de Renda")
    
    
    for tick in ax.get_xticklabels():
        tick.set_rotation(0)
        
    fig.tight_layout()
    canvas.draw()

def exportar_dados():
    
    ra = combo_ra.get()
    df_filtrado = df_moradores if ra == "Todas as RAs" else df_moradores[df_moradores['localidade'] == ra]
        
   
    caminho = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("Arquivos CSV", "*.csv")],
                                           title="Salvar dados filtrados")
    if caminho:
        df_filtrado.to_csv(caminho, index=False)
        messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{caminho}")


janela = tk.Tk()
janela.title("Explorador PDAD 2024 - Saúde e Serviços")
janela.geometry("800x650")


df_moradores = carregar_dados()


tk.Label(janela, text="Recorte C: Saúde e Acesso a Serviços", font=("Arial", 16, "bold")).pack(pady=10)
tk.Label(janela, text=f"Registros carregados: {len(df_moradores)} moradores", fg="gray").pack()


frame_controles = tk.Frame(janela)
frame_controles.pack(pady=15)

tk.Label(frame_controles, text="Filtrar por RA:").grid(row=0, column=0, padx=5)
ras_disponiveis = ["Todas as RAs"] + sorted(df_moradores['localidade'].unique().tolist())
combo_ra = ttk.Combobox(frame_controles, values=ras_disponiveis, state="readonly", width=25)
combo_ra.current(0)
combo_ra.grid(row=0, column=1, padx=5)

combo_ra.bind("<<ComboboxSelected>>", atualizar_interface)

btn_exportar = tk.Button(frame_controles, text="Exportar Dados (CSV)", command=exportar_dados, bg="#e0e0e0")
btn_exportar.grid(row=0, column=2, padx=20)


frame_stats = tk.Frame(janela, relief="groove", borderwidth=2)
frame_stats.pack(pady=10, fill=tk.X, padx=50)
lbl_stats = tk.Label(frame_stats, text="", font=("Arial", 11), justify="center", pady=10)
lbl_stats.pack()


frame_grafico = tk.Frame(janela)
frame_grafico.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


atualizar_interface()


janela.mainloop()