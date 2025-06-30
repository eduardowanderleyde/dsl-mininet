#!/bin/bash

# Script para configurar sudo sem senha para o usuário eduardo-wanderley
# Deve ser executado na VM como root ou com sudo

echo "Configurando sudo sem senha para eduardo-wanderley..."

# Verificar se já está configurado
if grep -q "eduardo-wanderley ALL=(ALL) NOPASSWD:ALL" /etc/sudoers; then
    echo "✓ Configuração já existe no sudoers"
    exit 0
fi

# Fazer backup do sudoers
cp /etc/sudoers /etc/sudoers.backup.$(date +%Y%m%d_%H%M%S)

# Adicionar configuração
echo "eduardo-wanderley ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Verificar se a sintaxe está correta
if visudo -c; then
    echo "✓ Configuração adicionada com sucesso"
    echo "✓ Teste com: sudo -n whoami"
else
    echo "✗ Erro na sintaxe do sudoers, restaurando backup..."
    cp /etc/sudoers.backup.* /etc/sudoers
    exit 1
fi 