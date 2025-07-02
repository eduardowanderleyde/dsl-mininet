#!/usr/bin/env python3
"""
Gerador de Relatórios Automático para DSL Mininet-WiFi
Versão 1.0 - Gera relatórios em PDF, HTML e Excel
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import os
import argparse
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import base64
from io import BytesIO

class ReportGenerator:
    """Gerador de relatórios automático"""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.data = {}
        
    def load_simulation_data(self, scenario_name: str) -> bool:
        """Carrega dados de simulação de um cenário"""
        if not os.path.exists(self.results_dir):
            print(f"❌ Diretório {self.results_dir} não encontrado!")
            return False
        
        # Procurar por arquivos do cenário
        scenario_files = []
        for file in os.listdir(self.results_dir):
            if file.startswith(scenario_name) and file.endswith('.csv'):
                scenario_files.append(file)
        
        if not scenario_files:
            print(f"❌ Nenhum arquivo encontrado para cenário: {scenario_name}")
            return False
        
        self.data[scenario_name] = {}
        
        for file in scenario_files:
            station_name = file.replace('.csv', '').replace(f'{scenario_name}_', '')
            file_path = os.path.join(self.results_dir, file)
            
            try:
                df = pd.read_csv(file_path)
                self.data[scenario_name][station_name] = df
                print(f"✅ Carregado: {file} ({len(df)} registros)")
            except Exception as e:
                print(f"❌ Erro ao carregar {file}: {e}")
        
        return True
    
    def generate_executive_summary(self, scenario_name: str) -> Dict:
        """Gera resumo executivo dos dados"""
        if scenario_name not in self.data:
            return {}
        
        summary = {
            'scenario_name': scenario_name,
            'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'total_stations': len(self.data[scenario_name]),
            'total_measurements': sum(len(df) for df in self.data[scenario_name].values()),
            'performance_metrics': {},
            'coverage_analysis': {},
            'recommendations': []
        }
        
        # Métricas de performance
        all_rssi = []
        all_latency = []
        
        for station_name, df in self.data[scenario_name].items():
            if 'rssi' in df.columns:
                all_rssi.extend(df['rssi'].tolist())
            if 'latency_ms' in df.columns:
                all_latency.extend(df['latency_ms'].tolist())
        
        if all_rssi:
            summary['performance_metrics']['rssi'] = {
                'mean': np.mean(all_rssi),
                'min': np.min(all_rssi),
                'max': np.max(all_rssi),
                'std': np.std(all_rssi),
                'excellent_count': len([r for r in all_rssi if r >= -50]),
                'good_count': len([r for r in all_rssi if -60 <= r < -50]),
                'fair_count': len([r for r in all_rssi if -70 <= r < -60]),
                'poor_count': len([r for r in all_rssi if r < -70])
            }
        
        if all_latency:
            summary['performance_metrics']['latency'] = {
                'mean': np.mean(all_latency),
                'min': np.min(all_latency),
                'max': np.max(all_latency),
                'std': np.std(all_latency)
            }
        
        # Análise de cobertura
        if all_rssi:
            rssi_metrics = summary['performance_metrics']['rssi']
            total_points = len(all_rssi)
            
            summary['coverage_analysis'] = {
                'excellent_coverage_percent': (rssi_metrics['excellent_count'] / total_points) * 100,
                'good_coverage_percent': (rssi_metrics['good_count'] / total_points) * 100,
                'fair_coverage_percent': (rssi_metrics['fair_count'] / total_points) * 100,
                'poor_coverage_percent': (rssi_metrics['poor_count'] / total_points) * 100,
                'overall_quality': self._get_overall_quality(rssi_metrics['mean'])
            }
        
        # Recomendações
        if all_rssi:
            rssi_mean = np.mean(all_rssi)
            if rssi_mean < -70:
                summary['recommendations'].append("Reposicionar APs para melhorar cobertura")
            elif rssi_mean < -60:
                summary['recommendations'].append("Considerar adicionar mais APs")
            else:
                summary['recommendations'].append("Cobertura adequada mantida")
        
        if all_latency:
            latency_mean = np.mean(all_latency)
            if latency_mean > 100:
                summary['recommendations'].append("Investigar causas de alta latência")
            elif latency_mean > 50:
                summary['recommendations'].append("Monitorar latência da rede")
            else:
                summary['recommendations'].append("Latência dentro dos parâmetros aceitáveis")
        
        return summary
    
    def _get_overall_quality(self, rssi_mean: float) -> str:
        """Determina qualidade geral baseada no RSSI médio"""
        if rssi_mean >= -50:
            return "Excelente"
        elif rssi_mean >= -60:
            return "Muito Boa"
        elif rssi_mean >= -70:
            return "Boa"
        elif rssi_mean >= -80:
            return "Regular"
        else:
            return "Ruim"
    
    def generate_charts(self, scenario_name: str) -> Dict:
        """Gera gráficos para o relatório"""
        if scenario_name not in self.data:
            return {}
        
        charts = {}
        
        # Gráfico de RSSI por station
        plt.figure(figsize=(12, 6))
        for station_name, df in self.data[scenario_name].items():
            if 'rssi' in df.columns:
                plt.plot(range(len(df)), df['rssi'], label=station_name, marker='o', markersize=4)
        
        plt.title('RSSI ao Longo do Tempo por Station', fontsize=14, fontweight='bold')
        plt.xlabel('Medição', fontsize=12)
        plt.ylabel('RSSI (dBm)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Salvar gráfico como base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        charts['rssi_timeline'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Gráfico de latência por station
        plt.figure(figsize=(12, 6))
        for station_name, df in self.data[scenario_name].items():
            if 'latency_ms' in df.columns:
                plt.plot(range(len(df)), df['latency_ms'], label=station_name, marker='s', markersize=4)
        
        plt.title('Latência ao Longo do Tempo por Station', fontsize=14, fontweight='bold')
        plt.xlabel('Medição', fontsize=12)
        plt.ylabel('Latência (ms)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        charts['latency_timeline'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Histograma de RSSI
        plt.figure(figsize=(10, 6))
        all_rssi = []
        for df in self.data[scenario_name].values():
            if 'rssi' in df.columns:
                all_rssi.extend(df['rssi'].tolist())
        
        if all_rssi:
            plt.hist(all_rssi, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Distribuição de RSSI', fontsize=14, fontweight='bold')
            plt.xlabel('RSSI (dBm)', fontsize=12)
            plt.ylabel('Frequência', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            charts['rssi_distribution'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        
        return charts
    
    def generate_html_report(self, scenario_name: str, output_file: str = None) -> str:
        """Gera relatório HTML interativo"""
        summary = self.generate_executive_summary(scenario_name)
        charts = self.generate_charts(scenario_name)
        
        # Template HTML
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Performance - {{ summary.scenario_name }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #666;
            margin: 5px 0;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metrics-section {
            margin-bottom: 30px;
        }
        .metrics-section h2 {
            color: #333;
            border-left: 4px solid #007bff;
            padding-left: 15px;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .metrics-table th, .metrics-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .metrics-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .chart-container {
            text-align: center;
            margin: 30px 0;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .recommendations {
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #2196f3;
        }
        .recommendations h3 {
            color: #1976d2;
            margin-top: 0;
        }
        .recommendations ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .recommendations li {
            margin: 5px 0;
        }
        .quality-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }
        .quality-excellent { background-color: #4caf50; }
        .quality-good { background-color: #8bc34a; }
        .quality-fair { background-color: #ff9800; }
        .quality-poor { background-color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Relatório de Performance</h1>
            <p><strong>Cenário:</strong> {{ summary.scenario_name }}</p>
            <p><strong>Gerado em:</strong> {{ summary.generation_date }}</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <h3>📡 Stations</h3>
                <div class="value">{{ summary.total_stations }}</div>
                <p>Total de estações</p>
            </div>
            <div class="summary-card">
                <h3>📊 Medições</h3>
                <div class="value">{{ summary.total_measurements }}</div>
                <p>Total de medições</p>
            </div>
            <div class="summary-card">
                <h3>📶 Qualidade</h3>
                <div class="value">{{ summary.coverage_analysis.overall_quality }}</div>
                <p>Qualidade geral</p>
            </div>
            <div class="summary-card">
                <h3>📈 Cobertura</h3>
                <div class="value">{{ "%.1f"|format(summary.coverage_analysis.excellent_coverage_percent) }}%</div>
                <p>Excelente</p>
            </div>
        </div>

        <div class="metrics-section">
            <h2>📊 Métricas de Performance</h2>
            
            {% if summary.performance_metrics.rssi %}
            <h3>📶 RSSI (Força do Sinal)</h3>
            <table class="metrics-table">
                <tr>
                    <th>Métrica</th>
                    <th>Valor</th>
                    <th>Descrição</th>
                </tr>
                <tr>
                    <td>Média</td>
                    <td>{{ "%.1f"|format(summary.performance_metrics.rssi.mean) }} dBm</td>
                    <td>RSSI médio de todas as medições</td>
                </tr>
                <tr>
                    <td>Mínimo</td>
                    <td>{{ "%.1f"|format(summary.performance_metrics.rssi.min) }} dBm</td>
                    <td>Menor valor de RSSI registrado</td>
                </tr>
                <tr>
                    <td>Máximo</td>
                    <td>{{ "%.1f"|format(summary.performance_metrics.rssi.max) }} dBm</td>
                    <td>Maior valor de RSSI registrado</td>
                </tr>
                <tr>
                    <td>Desvio Padrão</td>
                    <td>{{ "%.1f"|format(summary.performance_metrics.rssi.std) }} dBm</td>
                    <td>Variabilidade do sinal</td>
                </tr>
            </table>
            {% endif %}

            {% if summary.performance_metrics.latency %}
            <h3>⏱️ Latência</h3>
            <table class="metrics-table">
                <tr>
                    <th>Métrica</th>
                    <th>Valor</th>
                    <th>Descrição</th>
                </tr>
                <tr>
                    <td>Média</td>
                    <td>{{ "%.3f"|format(summary.performance_metrics.latency.mean) }} ms</td>
                    <td>Latência média de todas as medições</td>
                </tr>
                <tr>
                    <td>Mínima</td>
                    <td>{{ "%.3f"|format(summary.performance_metrics.latency.min) }} ms</td>
                    <td>Menor latência registrada</td>
                </tr>
                <tr>
                    <td>Máxima</td>
                    <td>{{ "%.3f"|format(summary.performance_metrics.latency.max) }} ms</td>
                    <td>Maior latência registrada</td>
                </tr>
                <tr>
                    <td>Desvio Padrão</td>
                    <td>{{ "%.3f"|format(summary.performance_metrics.latency.std) }} ms</td>
                    <td>Variabilidade da latência</td>
                </tr>
            </table>
            {% endif %}
        </div>

        {% if charts %}
        <div class="metrics-section">
            <h2>📈 Gráficos de Análise</h2>
            
            {% if charts.rssi_timeline %}
            <div class="chart-container">
                <h3>RSSI ao Longo do Tempo</h3>
                <img src="data:image/png;base64,{{ charts.rssi_timeline }}" alt="RSSI Timeline">
            </div>
            {% endif %}

            {% if charts.latency_timeline %}
            <div class="chart-container">
                <h3>Latência ao Longo do Tempo</h3>
                <img src="data:image/png;base64,{{ charts.latency_timeline }}" alt="Latency Timeline">
            </div>
            {% endif %}

            {% if charts.rssi_distribution %}
            <div class="chart-container">
                <h3>Distribuição de RSSI</h3>
                <img src="data:image/png;base64,{{ charts.rssi_distribution }}" alt="RSSI Distribution">
            </div>
            {% endif %}
        </div>
        {% endif %}

        {% if summary.recommendations %}
        <div class="recommendations">
            <h3>💡 Recomendações</h3>
            <ul>
                {% for recommendation in summary.recommendations %}
                <li>{{ recommendation }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(summary=summary, charts=charts)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Relatório HTML salvo em: {output_file}")
        
        return html_content
    
    def export_to_excel(self, scenario_name: str, output_file: str = None) -> bool:
        """Exporta dados para Excel com múltiplas abas"""
        if scenario_name not in self.data:
            print(f"❌ Cenário {scenario_name} não encontrado!")
            return False
        
        if not output_file:
            output_file = f"relatorio_{scenario_name}.xlsx"
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Aba 1: Dados brutos por station
                for station_name, df in self.data[scenario_name].items():
                    df.to_excel(writer, sheet_name=f'Station_{station_name}', index=False)
                
                # Aba 2: Resumo executivo
                summary = self.generate_executive_summary(scenario_name)
                summary_data = []
                
                # Métricas de RSSI
                if 'rssi' in summary['performance_metrics']:
                    rssi_metrics = summary['performance_metrics']['rssi']
                    summary_data.extend([
                        ['Métrica', 'Valor', 'Unidade'],
                        ['RSSI Médio', f"{rssi_metrics['mean']:.1f}", 'dBm'],
                        ['RSSI Mínimo', f"{rssi_metrics['min']:.1f}", 'dBm'],
                        ['RSSI Máximo', f"{rssi_metrics['max']:.1f}", 'dBm'],
                        ['RSSI Desvio Padrão', f"{rssi_metrics['std']:.1f}", 'dBm'],
                        ['Cobertura Excelente', rssi_metrics['excellent_count'], 'pontos'],
                        ['Cobertura Boa', rssi_metrics['good_count'], 'pontos'],
                        ['Cobertura Regular', rssi_metrics['fair_count'], 'pontos'],
                        ['Cobertura Ruim', rssi_metrics['poor_count'], 'pontos']
                    ])
                
                # Métricas de latência
                if 'latency' in summary['performance_metrics']:
                    latency_metrics = summary['performance_metrics']['latency']
                    summary_data.extend([
                        ['', '', ''],
                        ['Latência Média', f"{latency_metrics['mean']:.3f}", 'ms'],
                        ['Latência Mínima', f"{latency_metrics['min']:.3f}", 'ms'],
                        ['Latência Máxima', f"{latency_metrics['max']:.3f}", 'ms'],
                        ['Latência Desvio Padrão', f"{latency_metrics['std']:.3f}", 'ms']
                    ])
                
                summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
                summary_df.to_excel(writer, sheet_name='Resumo_Executivo', index=False)
                
                # Aba 3: Análise de cobertura
                coverage_data = []
                for station_name, df in self.data[scenario_name].items():
                    if 'rssi' in df.columns:
                        station_stats = {
                            'Station': station_name,
                            'RSSI_Médio': df['rssi'].mean(),
                            'RSSI_Mín': df['rssi'].min(),
                            'RSSI_Máx': df['rssi'].max(),
                            'RSSI_Std': df['rssi'].std(),
                            'Medições': len(df)
                        }
                        coverage_data.append(station_stats)
                
                if coverage_data:
                    coverage_df = pd.DataFrame(coverage_data)
                    coverage_df.to_excel(writer, sheet_name='Análise_Cobertura', index=False)
                
                # Aba 4: Recomendações
                recommendations_data = [
                    ['Recomendação', 'Prioridade'],
                ]
                
                for i, rec in enumerate(summary['recommendations']):
                    priority = 'Alta' if i < 2 else 'Média'
                    recommendations_data.append([rec, priority])
                
                recommendations_df = pd.DataFrame(recommendations_data[1:], columns=recommendations_data[0])
                recommendations_df.to_excel(writer, sheet_name='Recomendações', index=False)
            
            print(f"✅ Relatório Excel salvo em: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório Excel: {e}")
            return False

def main():
    """Função principal para uso via linha de comando"""
    parser = argparse.ArgumentParser(description='Gerador de Relatórios Automático')
    parser.add_argument('action', choices=['html', 'excel'],
                       help='Tipo de relatório a gerar')
    parser.add_argument('--scenario', '-s', required=True, help='Nome do cenário')
    parser.add_argument('--output', '-o', help='Arquivo de saída')
    parser.add_argument('--results-dir', '-r', default='results', help='Diretório de resultados')
    
    args = parser.parse_args()
    
    generator = ReportGenerator(args.results_dir)
    
    if not generator.load_simulation_data(args.scenario):
        return
    
    if args.action == 'html':
        output_file = args.output or f"relatorio_{args.scenario}.html"
        generator.generate_html_report(args.scenario, output_file)
    
    elif args.action == 'excel':
        output_file = args.output or f"relatorio_{args.scenario}.xlsx"
        generator.export_to_excel(args.scenario, output_file)

if __name__ == "__main__":
    main() 