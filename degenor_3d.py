bl_info = {
    "name": "Degenor.3D",
    "author": "Andressa Salgado",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Degenor",
    "description": "Gera órtese com furos esféricos com base em porcentagem de remoção",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
import random
import math
import os

# -------------------- FUNÇÕES DO GERADOR --------------------
def criar_retangulo(comprimento, largura, espessura):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    retangulo = bpy.context.object
    retangulo.scale = (comprimento, largura, espessura)
    retangulo.name = "Retangulo_Base"
    return retangulo

def calcular_volume_esfera(raio):
    return (4/3) * math.pi * (raio ** 3)

def gerar_pontos_semente(volume_retangulo, remocao_percentual, comprimento, largura, espessura):
    volume_removido_alvo = (remocao_percentual / 100) * volume_retangulo
    volume_atual_removido = 0
    pontos = []
    tentativas_total = 0
    max_tentativas_total = 100000 
    tentativa_batch = 0
    max_batch = 10000

    while volume_atual_removido < volume_removido_alvo and tentativas_total < max_tentativas_total:
        raio_esfera = random.uniform(0.0005, 0.001)  # 0.05 cm a 0.1 cm em metros
        volume_esfera = calcular_volume_esfera(raio_esfera)

        x_novo = random.uniform(-comprimento + raio_esfera, comprimento - raio_esfera)
        y_novo = random.uniform(-largura + raio_esfera, largura - raio_esfera)
        z_novo = random.uniform(-espessura, espessura)

        colisao = any(
            math.sqrt((x - x_novo) ** 2 + (y - y_novo) ** 2 + (z - z_novo) ** 2) < (r + raio_esfera + 0.0002)
            for x, y, z, r in pontos
        )

        if not colisao and volume_atual_removido + volume_esfera <= volume_removido_alvo:
            pontos.append((x_novo, y_novo, z_novo, raio_esfera))
            volume_atual_removido += volume_esfera
            tentativa_batch = 0 
        else:
            tentativa_batch += 1

        tentativas_total += 1

        if tentativa_batch > max_batch:
            print("Muitas tentativas sem sucesso. Encerrando antes do tempo.")
            break

    print(f"Volume total removido: {volume_atual_removido:.5f} m³ (Meta: {volume_removido_alvo:.5f} m³)")
    print(f"Esferas criadas: {len(pontos)}")
    return pontos


def criar_esferas(pontos):
    esferas = []
    for ponto in pontos:
        x, y, z, raio = ponto
        bpy.ops.mesh.primitive_uv_sphere_add(radius=raio, location=(x, y, z))
        esfera = bpy.context.object
        esferas.append(esfera)
    return esferas

def aplicar_boolean_subtracao(obj_base, objetos_corte):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objetos_corte:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objetos_corte[0]
    bpy.ops.object.join()
    esfera_unida = bpy.context.object

    bpy.context.view_layer.objects.active = obj_base
    esfera_unida.select_set(True)
    obj_base.select_set(True)

    mod_bool = obj_base.modifiers.new(name="Boolean", type='BOOLEAN')
    mod_bool.object = esfera_unida
    mod_bool.operation = 'DIFFERENCE'
    bpy.ops.object.modifier_apply(modifier=mod_bool.name)

    bpy.data.objects.remove(esfera_unida, do_unlink=True)

def exportar_stl(obj, filepath):
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True, global_scale=1000)

# -------------------- OPERADOR PRINCIPAL --------------------
class OrtopediaGeneratorOperator(bpy.types.Operator):
    bl_idname = "object.gerar_ortese"
    bl_label = "Gerar Órtese"

    def execute(self, context):
        # Converte de centímetros para metros
        comprimento = context.scene.ortese_comprimento / 100
        largura = context.scene.ortese_largura / 100
        espessura = context.scene.ortese_espessura / 100
        remocao = context.scene.ortese_remocao
        nome_arquivo = context.scene.ortese_nome_arquivo

        retangulo = criar_retangulo(comprimento, largura, espessura)
        volume_retangulo = comprimento * largura * espessura
        pontos = gerar_pontos_semente(volume_retangulo, remocao, comprimento, largura, espessura)
        esferas = criar_esferas(pontos)
        aplicar_boolean_subtracao(retangulo, esferas)

        caminho = os.path.join(os.path.expanduser("~"), "Downloads", f"{nome_arquivo}.stl")
        exportar_stl(retangulo, caminho)
        self.report({'INFO'}, f"Arquivo STL exportado para: {caminho}")

        return {'FINISHED'}

# -------------------- INTERFACE NO PAINEL --------------------
class OrtopediaPainel(bpy.types.Panel):
    bl_label = "Gerador de Órtese"
    bl_idname = "PT_DegenorPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Degenor"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "ortese_comprimento")
        layout.prop(scene, "ortese_largura")
        layout.prop(scene, "ortese_espessura")
        layout.prop(scene, "ortese_remocao")
        layout.prop(scene, "ortese_nome_arquivo")

        layout.operator("object.gerar_ortese")

# -------------------- REGISTRO --------------------
classes = [OrtopediaGeneratorOperator, OrtopediaPainel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ortese_comprimento = bpy.props.FloatProperty(name="Comprimento (cm)", default=50.0, min=0.1)
    bpy.types.Scene.ortese_largura = bpy.props.FloatProperty(name="Largura (cm)", default=130.0, min=0.1)
    bpy.types.Scene.ortese_espessura = bpy.props.FloatProperty(name="Espessura (cm)", default=0.08, min=0.01)
    bpy.types.Scene.ortese_remocao = bpy.props.FloatProperty(name="Remoção (%)", default=50.0, min=0.1, max=100.0)
    bpy.types.Scene.ortese_nome_arquivo = bpy.props.StringProperty(name="Nome do Arquivo STL", default="ortese_modelo")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ortese_comprimento
    del bpy.types.Scene.ortese_largura
    del bpy.types.Scene.ortese_espessura
    del bpy.types.Scene.ortese_remocao
    del bpy.types.Scene.ortese_nome_arquivo

if __name__ == "__main__":
    register()
