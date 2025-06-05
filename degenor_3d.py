bl_info = {
    "name": "Degenor.3D",
    "author": "Andressa Salgado",
    "version": (1, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Degenor",
    "description": "Gera órtese com furos cilíndricos com base em porcentagem de remoção",
    "doc_url": "https://github.com/andressasalgado/degenor.3d",
    "category": "Object",
}

import bpy
import random
import math
import os
from mathutils import Vector, kdtree

# -------------------- GESTÃO DE COLEÇÕES --------------------

# Cria uma nova coleção no Blender ou obtém uma existente
def obter_ou_criar_colecao(nome):
    if nome in bpy.data.collections:
        return bpy.data.collections[nome]
    else:
        colecao = bpy.data.collections.new(nome)
        bpy.context.scene.collection.children.link(colecao)
        return colecao

# Remove todos os objetos de uma coleção específica
def limpar_colecao(nome):
    if nome in bpy.data.collections:
        colecao = bpy.data.collections[nome]
        for obj in list(colecao.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

# -------------------- FUNÇÕES AUXILIARES --------------------

# Cria um retângulo 3D com os parâmetros de comprimento, largura e espessura
def criar_retangulo(comprimento, largura, espessura, nome="Retangulo", colecao=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    cubo = bpy.context.active_object
    cubo.scale = (comprimento, largura, espessura)
    cubo.name = nome

    if colecao:
        colecao.objects.link(cubo)
        if cubo.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(cubo)

    return cubo

def criar_cilindro(raio, altura, localizacao, nome, colecao):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=raio,
        depth=altura,
        location=localizacao
    )
    cilindro = bpy.context.active_object
    cilindro.name = nome

    if colecao:
        colecao.objects.link(cilindro)
        if cilindro.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(cilindro)

    return cilindro

def calcular_volume_cilindro(raio, altura):
    return math.pi * (raio ** 2) * altura

def gerar_pontos_semente(volume_retangulo, remocao_percentual, comprimento, largura, espessura):
    volume_removido_alvo = (remocao_percentual / 100) * volume_retangulo
    volume_atual_removido = 0
    pontos = []

    max_tentativas = 150000
    tentativas = 0

    usa_kdtree = False
    tree = None

    while volume_atual_removido < volume_removido_alvo and tentativas < max_tentativas:
        # Alternar tamanhos de furos dependendo de % já removido
        percentual_atual = (volume_atual_removido / volume_removido_alvo) * 100

        if percentual_atual <= 50:
            raio = random.uniform(0.0015, 0.0025)  # Furos grandes
        elif percentual_atual <= 75:
            raio = random.uniform(0.0012, 0.0018)  # Furos médios
        else:
            raio = random.uniform(0.0008, 0.0012)  # Furos pequenos

        volume_cilindro = calcular_volume_cilindro(raio, espessura)

        x = random.uniform(-comprimento/2 + raio, comprimento/2 - raio)
        y = random.uniform(-largura/2 + raio, largura/2 - raio)
        z = 0  # Cilindros atravessam a altura

        novo_ponto = Vector((x, y, z))

        colisao = False
        if pontos:
            if not usa_kdtree:
                tree = kdtree.KDTree(len(pontos))
                for idx, (p, _) in enumerate(pontos):
                    tree.insert(p, idx)
                tree.balance()
                usa_kdtree = True

            for (co, idx, dist) in tree.find_range(novo_ponto, raio + 0.004):
                p2, r2 = pontos[idx]
                if (novo_ponto - p2).length < (raio + r2 + 0.0002):
                    colisao = True
                    break

        if not colisao and (volume_atual_removido + volume_cilindro) <= volume_removido_alvo:
            pontos.append((novo_ponto, raio))
            volume_atual_removido += volume_cilindro
            usa_kdtree = False

        tentativas += 1

    return pontos

# Cria cilindros nos pontos de semente gerados
def criar_cilindros(pontos, altura, colecao):
    cilindros = []
    for idx, (ponto, raio) in enumerate(pontos):
        cilindro = criar_cilindro(raio, altura + 0.001, ponto, f"Furo_{idx}", colecao)
        cilindros.append(cilindro)
    return cilindros

# Aplica uma operação booleana de subtração de múltiplos objetos (cortadores) sobre uma base
def aplicar_boolean_subtracao(base, cortadores):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in cortadores:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = cortadores[0]
    bpy.ops.object.join()
    unido = bpy.context.active_object

    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    mod = base.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.object = unido
    mod.operation = 'DIFFERENCE'
    bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.data.objects.remove(unido, do_unlink=True)

# Aplica uma operação booleana de diferença entre dois objetos
def aplicar_boolean_diferenca(objeto_base, objeto_corte):
    mod = objeto_base.modifiers.new(name="BooleanMargin", type='BOOLEAN')
    mod.object = objeto_corte
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = objeto_base
    bpy.ops.object.modifier_apply(modifier=mod.name)

# -------------------- CRIAR MARGEM --------------------

# Cria a margem (moldura) externa da órtese, que delimita a peça
def criar_margem(comprimento, largura, espessura, colecao):
    # Cria a margem externa (um pouco maior que a base)
    margem_externa = criar_retangulo(comprimento + 0.01, largura + 0.0008, espessura, "Margem_Externa", colecao)

    corte_interno = criar_retangulo(comprimento, largura, espessura + 0.001, "Corte_Interno", colecao)
    aplicar_boolean_diferenca(margem_externa, corte_interno)
    bpy.data.objects.remove(corte_interno, do_unlink=True)

    buraco_largura = max(largura - 0.004, 0.007)

    buraco1 = criar_retangulo(0.006, buraco_largura, espessura + 0.003, "Buraco1", colecao)
    buraco1.location = (-(comprimento + 0.01) / 2 + 0.005, 0, 0)

    buraco2 = criar_retangulo(0.006, buraco_largura, espessura + 0.003, "Buraco2", colecao)
    buraco2.location = ((comprimento + 0.01) / 2 - 0.005, 0, 0)

    aplicar_boolean_diferenca(margem_externa, buraco1)
    aplicar_boolean_diferenca(margem_externa, buraco2)

    bpy.data.objects.remove(buraco1, do_unlink=True)
    bpy.data.objects.remove(buraco2, do_unlink=True)

    return margem_externa

# -------------------- EXPORTAR STL --------------------

# Exporta o objeto 3D como um arquivo STL
def exportar_stl(obj, caminho):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_mesh.stl(filepath=caminho, use_selection=True, global_scale=1000)

# -------------------- OPERADOR PRINCIPAL --------------------

# Operador principal que gera a órtese através da interface do Blender
class GeradorOrteseOperator(bpy.types.Operator):
    bl_idname = "object.gerar_ortese"
    bl_label = "Gerar Órtese"

    def execute(self, context):
        comprimento = context.scene.ortese_comprimento / 100
        largura = context.scene.ortese_largura / 100
        espessura = 0.0008

        remocao = context.scene.ortese_remocao
        nome_arquivo = context.scene.ortese_nome_arquivo

        colecao = obter_ou_criar_colecao("Ortese_Gerada")
        limpar_colecao("Ortese_Gerada")

        retangulo = criar_retangulo(comprimento, largura, espessura, "Ortese_Base", colecao)
        volume_retangulo = comprimento * largura * espessura

        pontos = gerar_pontos_semente(volume_retangulo, remocao, comprimento, largura, espessura)
        cilindros = criar_cilindros(pontos, espessura, colecao)
        aplicar_boolean_subtracao(retangulo, cilindros)

        margem = criar_margem(comprimento, largura, espessura, colecao)

        bpy.ops.object.select_all(action='DESELECT')
        retangulo.select_set(True)
        margem.select_set(True)
        bpy.context.view_layer.objects.active = margem
        bpy.ops.object.join()

        caminho = os.path.join(os.path.expanduser("~"), "Downloads", f"{nome_arquivo}.stl")
        exportar_stl(margem, caminho)
        self.report({'INFO'}, f"Arquivo STL exportado para: {caminho}")

        return {'FINISHED'}

# Operador que limpa a cena ou a coleção, removendo os objetos da órtese
class LimparOrteseOperator(bpy.types.Operator):
    bl_idname = "object.limpar_ortese"
    bl_label = "Limpar Órtese"

    def execute(self, context):
        limpar_colecao("Ortese_Gerada")
        self.report({'INFO'}, "Ortese removida da cena")
        return {'FINISHED'}

# -------------------- INTERFACE --------------------

# Define o painel na interface do Blender para interação com o plugin
class DegenorPainel(bpy.types.Panel):
    bl_label = "Gerador de Órtese"
    bl_idname = "PT_DegenorPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Degenor V3.5"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "ortese_comprimento")
        layout.prop(context.scene, "ortese_largura")
        layout.prop(context.scene, "ortese_remocao")
        layout.prop(context.scene, "ortese_nome_arquivo")
        layout.operator("object.gerar_ortese")
        layout.operator("object.limpar_ortese")

# -------------------- REGISTRO --------------------

classes = [GeradorOrteseOperator, LimparOrteseOperator, DegenorPainel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ortese_comprimento = bpy.props.FloatProperty(name="Comprimento (cm)", default=13.0)
    bpy.types.Scene.ortese_largura = bpy.props.FloatProperty(name="Largura (cm)", default=5.0)
    bpy.types.Scene.ortese_remocao = bpy.props.FloatProperty(name="Remoção (%)", default=40.0)
    bpy.types.Scene.ortese_nome_arquivo = bpy.props.StringProperty(name="Nome do Arquivo STL", default="ortese_modelo")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ortese_comprimento
    del bpy.types.Scene.ortese_largura
    del bpy.types.Scene.ortese_remocao
    del bpy.types.Scene.ortese_nome_arquivo

if __name__ == "__main__":
    register()
