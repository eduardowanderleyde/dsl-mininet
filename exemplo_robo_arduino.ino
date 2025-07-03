/*
 * Código Arduino para Robô WiFi Tester
 * Recebe comandos via Serial e executa movimentos
 * Compatível com o sistema DSL Mininet-WiFi v4.0
 */

#include <SoftwareSerial.h>

// Configurações do robô
const int MOTOR_ESQUERDA_FRENTE = 5;
const int MOTOR_ESQUERDA_TRAS = 6;
const int MOTOR_DIREITA_FRENTE = 9;
const int MOTOR_DIREITA_TRAS = 10;

// Configurações de movimento
const int VELOCIDADE_PADRAO = 150;
const int TEMPO_MOVIMENTO = 1000; // ms

// Variáveis globais
String comando_recebido = "";
float posicao_x = 0;
float posicao_y = 0;

void setup() {
  // Inicializar comunicação serial
  Serial.begin(9600);
  Serial.println("🤖 Robô WiFi Tester Iniciado");
  Serial.println("📡 Pronto para receber comandos");
  
  // Configurar pinos dos motores
  pinMode(MOTOR_ESQUERDA_FRENTE, OUTPUT);
  pinMode(MOTOR_ESQUERDA_TRAS, OUTPUT);
  pinMode(MOTOR_DIREITA_FRENTE, OUTPUT);
  pinMode(MOTOR_DIREITA_TRAS, OUTPUT);
  
  // Parar motores
  parar_motores();
}

void loop() {
  // Verificar se há comandos disponíveis
  if (Serial.available() > 0) {
    comando_recebido = Serial.readStringUntil('\n');
    comando_recebido.trim();
    
    Serial.print("📥 Comando recebido: ");
    Serial.println(comando_recebido);
    
    // Processar comando
    processar_comando(comando_recebido);
  }
}

void processar_comando(String comando) {
  // Comando de teste
  if (comando == "TEST") {
    Serial.println("✅ Robô funcionando!");
    return;
  }
  
  // Comando de movimento: MOVE x y
  if (comando.startsWith("MOVE")) {
    // Parsear coordenadas
    int primeiro_espaco = comando.indexOf(' ');
    int segundo_espaco = comando.indexOf(' ', primeiro_espaco + 1);
    
    if (primeiro_espaco != -1 && segundo_espaco != -1) {
      float x = comando.substring(primeiro_espaco + 1, segundo_espaco).toFloat();
      float y = comando.substring(segundo_espaco + 1).toFloat();
      
      mover_para_posicao(x, y);
    }
    return;
  }
  
  // Comando de parada
  if (comando == "STOP") {
    parar_motores();
    Serial.println("🛑 Robô parado");
    return;
  }
  
  // Comando de status
  if (comando == "STATUS") {
    Serial.print("📍 Posição atual: (");
    Serial.print(posicao_x);
    Serial.print(", ");
    Serial.print(posicao_y);
    Serial.println(")");
    return;
  }
  
  // Comando não reconhecido
  Serial.print("❌ Comando não reconhecido: ");
  Serial.println(comando);
}

void mover_para_posicao(float x_destino, float y_destino) {
  Serial.print("🚗 Movendo para (");
  Serial.print(x_destino);
  Serial.print(", ");
  Serial.print(y_destino);
  Serial.println(")");
  
  // Calcular direção
  float delta_x = x_destino - posicao_x;
  float delta_y = y_destino - posicao_y;
  
  // Determinar movimento
  if (abs(delta_x) > abs(delta_y)) {
    // Movimento horizontal
    if (delta_x > 0) {
      mover_frente();
    } else {
      mover_tras();
    }
  } else {
    // Movimento vertical
    if (delta_y > 0) {
      mover_direita();
    } else {
      mover_esquerda();
    }
  }
  
  // Aguardar movimento
  delay(TEMPO_MOVIMENTO);
  
  // Parar
  parar_motores();
  
  // Atualizar posição
  posicao_x = x_destino;
  posicao_y = y_destino;
  
  Serial.println("✅ Movimento concluído");
}

void mover_frente() {
  analogWrite(MOTOR_ESQUERDA_FRENTE, VELOCIDADE_PADRAO);
  analogWrite(MOTOR_ESQUERDA_TRAS, 0);
  analogWrite(MOTOR_DIREITA_FRENTE, VELOCIDADE_PADRAO);
  analogWrite(MOTOR_DIREITA_TRAS, 0);
}

void mover_tras() {
  analogWrite(MOTOR_ESQUERDA_FRENTE, 0);
  analogWrite(MOTOR_ESQUERDA_TRAS, VELOCIDADE_PADRAO);
  analogWrite(MOTOR_DIREITA_FRENTE, 0);
  analogWrite(MOTOR_DIREITA_TRAS, VELOCIDADE_PADRAO);
}

void mover_esquerda() {
  analogWrite(MOTOR_ESQUERDA_FRENTE, 0);
  analogWrite(MOTOR_ESQUERDA_TRAS, VELOCIDADE_PADRAO);
  analogWrite(MOTOR_DIREITA_FRENTE, VELOCIDADE_PADRAO);
  analogWrite(MOTOR_DIREITA_TRAS, 0);
}

void mover_direita() {
  analogWrite(MOTOR_ESQUERDA_FRENTE, VELOCIDADE_PADRAO);
  analogWrite(MOTOR_ESQUERDA_TRAS, 0);
  analogWrite(MOTOR_DIREITA_FRENTE, 0);
  analogWrite(MOTOR_DIREITA_TRAS, VELOCIDADE_PADRAO);
}

void parar_motores() {
  analogWrite(MOTOR_ESQUERDA_FRENTE, 0);
  analogWrite(MOTOR_ESQUERDA_TRAS, 0);
  analogWrite(MOTOR_DIREITA_FRENTE, 0);
  analogWrite(MOTOR_DIREITA_TRAS, 0);
} 