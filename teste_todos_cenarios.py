#!/usr/bin/env python3
"""
Script para testar rapidamente todos os cenários corrigidos
Verifica se todos os nomes de stations estão corretos
"""

import json
import os
import glob

def verificar_cenario(arquivo):
    """Verifica se um cenário tem nomes válidos de stations"""
    try:
        with open(arquivo, 'r') as f:
            config = json.load(f)
        
        stations = config.get('stations', [])
        problemas = []
        
        for i, sta in enumerate(stations):
            nome = sta.get('name', '')
            
            # Verificar se tem underscore (problemático)
            if '_' in nome:
                problemas.append(f"Station {i+1}: '{nome}' tem underscore")
            
            # Verificar se é nome válido
            if not nome or nome == '':
                problemas.append(f"Station {i+1}: nome vazio")
        
        if problemas:
            return False, problemas
        else:
            return True, []
            
    except Exception as e:
        return False, [f"Erro ao ler arquivo: {e}"]

def main():
    print("🔍 VERIFICANDO TODOS OS CENÁRIOS CORRIGIDOS")
    print("=" * 50)
    
    # Encontrar todos os arquivos JSON de cenários
    cenarios_files = []
    cenarios_files.extend(glob.glob("cenarios_novos/*.json"))
    cenarios_files.extend(glob.glob("cenarios/*.json"))
    
    total = len(cenarios_files)
    funcionais = 0
    problematicos = 0
    
    for arquivo in sorted(cenarios_files):
        print(f"\n📁 {arquivo}:")
        
        ok, problemas = verificar_cenario(arquivo)
        
        if ok:
            print("  ✅ Nomes válidos")
            funcionais += 1
        else:
            print("  ❌ Problemas encontrados:")
            for problema in problemas:
                print(f"    - {problema}")
            problematicos += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMO:")
    print(f"   Total de cenários: {total}")
    print(f"   ✅ Funcionais: {funcionais}")
    print(f"   ❌ Problemáticos: {problematicos}")
    
    if problematicos == 0:
        print("\n🎉 TODOS OS CENÁRIOS ESTÃO CORRETOS!")
        print("   Agora você pode executar qualquer cenário sem problemas de nomenclatura.")
    else:
        print(f"\n⚠️  Ainda há {problematicos} cenário(s) com problemas.")
        print("   Verifique os erros acima e corrija os nomes.")

if __name__ == "__main__":
    main() 