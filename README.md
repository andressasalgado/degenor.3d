# Degenor.3D
**Design Generativo de Órteses em Blender**

Degenor.3D é um plugin gratuito e open-source para Blender, desenvolvido para facilitar a criação automatizada de órteses personalizadas utilizando algoritmos de design generativo com padrão Voronoi. Ideal para aplicações biomédicas, prototipagem rápida e pesquisas em modelagem paramétrica.

---

## Recursos

- Geração automatizada de órteses com padrão Voronoi
- Personalização por parâmetros anatômicos
- Estruturas otimizadas: leveza, resistência e economia de material
- Script desenvolvido em Python, totalmente compatível com Blender 3.0+

---

## 📥 Instalação

1. Faça o download do repositório:
   ```bash
   git clone https://github.com/andressasalgado/degenor.3d.git
ou baixe o arquivo .py diretamente no botão Download raw file.

2. Abra o Blender.

3. No menu superior, acesse:
   Editar (Edit) > Preferências (Preferences).

4. No painel lateral, selecione: Add-ons.

5. Clique em Install... (Instalar).

6. Localize o arquivo do plugin (degenor_3d.py) no seu computador e selecione.

7. Marque a caixa de seleção ao lado do nome do plugin para ativá-lo.

## 🛠️ Como usar
1️⃣ Entendendo os parâmetros

O Degenor.3D permite que o usuário personalize a órtese a partir de três parâmetros principais:
- Largura (cm): Refere-se à extensão da área de cobertura da órtese, ou seja, o quanto ela se estende ao longo do braço.
- Comprimento (cm): Corresponde à circunferência do pulso.
- Porcentagem de remoção (%): Define o quanto de material será removido, criando os vazados no modelo. Maior valor = mais leve e mais ventilada; menor valor = mais robusta.

2️⃣ Como tirar medidas

🧰 Materiais: fita métrica flexível.

📏 Meça:
- Comprimento: Envolva a fita ao redor do pulso e anote a medida da circunferência.
- Largura: Meça o quanto a órtese deve cobrir no antebraço, no sentido longitudinal.
  
🎯 Escolha a porcentagem de remoção com base na sua preferência de estética, ventilação e resistência.

3️⃣ Gerando sua órtese no Blender

1. Acesse o painel lateral do Blender pressionando N.
2. Clique na aba Degenor.3D.
3. Insira os valores de:
   - Largura (cm)
   - Comprimento (cm)
   - Porcentagem de remoção (%)
4. Clique em "Gerar Órtese".

Opcional: Caso queira limpar a cena e começar novamente, utilize o botão "Limpar Cena".
