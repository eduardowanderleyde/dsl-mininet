#!/bin/bash

# Script para configurar sudo sem senha para o usuário eduardo-wanderley
# Deve ser executado na VM como root

echo "Configurando sudo sem senha para eduardo-wanderley..."

# Verificar se o arquivo sudoers já tem a configuração
if grep -q "eduardo-wanderley ALL=(ALL) NOPASSWD:ALL" /etc/sudoers; then
    echo "✓ Configuração já existe no sudoers"
else
    echo "Adicionando configuração ao sudoers..."
    echo "eduardo-wanderley ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
    echo "✓ Configuração adicionada"
fi

# Verificar se o grupo sudo existe e adicionar o usuário
if getent group sudo > /dev/null 2>&1; then
    usermod -aG sudo eduardo-wanderley
    echo "✓ Usuário adicionado ao grupo sudo"
else
    echo "⚠ Grupo sudo não encontrado"
fi

echo "Configuração concluída!"
echo "Teste com: sudo -n whoami" 