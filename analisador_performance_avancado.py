#!/usr/bin/env python3
"""
Analisador de Performance Avançado para DSL Mininet-WiFi
Versão 1.0 - Análise de cobertura, mapas de calor e detecção de anomalias
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import argparse
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PerformanceAnalyzer:
    """Analisador avançado de performance de redes WiFi"""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.data = {}
        self.scenarios = {}
        
    def load_data(self, scenario_name: str = None):
        """Carrega dados de um cenário específico ou todos os cenários"""
        if not os.path.exists(self.results_dir):
            print(f"❌ Diretório {self.results_dir} não encontrado!")
            return False
            
        if scenario_name:
            return self._load_single_scenario(scenario_name)
        else:
            return self._load_all_scenarios()
    
    def _load_single_scenario(self, scenario_name: str) -> bool:
        """Carrega dados de um cenário específico"""
        scenario_files = []
        
        # Procurar por arquivos do cenário
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
    
    def _load_all_scenarios(self) -> bool:
        """Carrega dados de todos os cenários disponíveis"""
        csv_files = [f for f in os.listdir(self.results_dir) if f.endswith('.csv')]
        
        if not csv_files:
            print(f"❌ Nenhum arquivo CSV encontrado em {self.results_dir}")
            return False
        
        # Agrupar por cenário
        scenarios = {}
        for file in csv_files:
            parts = file.replace('.csv', '').split('_')
            if len(parts) >= 2:
                scenario_name = '_'.join(parts[:-1])  # Tudo exceto última parte
                station_name = parts[-1]  # Última parte é o nome da station
                
                if scenario_name not in scenarios:
                    scenarios[scenario_name] = []
                scenarios[scenario_name].append((file, station_name))
        
        for scenario_name, files in scenarios.items():
            self.data[scenario_name] = {}
            for file, station_name in files:
                file_path = os.path.join(self.results_dir, file)
                try:
                    df = pd.read_csv(file_path)
                    self.data[scenario_name][station_name] = df
                except Exception as e:
                    print(f"❌ Erro ao carregar {file}: {e}")
        
        print(f"✅ Carregados {len(self.data)} cenários")
        return True
    
    def analyze_coverage(self, scenario_name: str) -> Dict:
        """Analisa cobertura da rede para um cenário"""
        if scenario_name not in self.data:
            print(f"❌ Cenário {scenario_name} não encontrado!")
            return {}
        
        coverage_analysis = {
            'scenario': scenario_name,
            'total_stations': len(self.data[scenario_name]),
            'coverage_stats': {},
            'dead_zones': [],
            'excellent_coverage': [],
            'poor_coverage': []
        }
        
        for station_name, df in self.data[scenario_name].items():
            if 'rssi' not in df.columns:
                continue
                
            # Estatísticas de RSSI
            rssi_stats = {
                'mean': df['rssi'].mean(),
                'min': df['rssi'].min(),
                'max': df['rssi'].max(),
                'std': df['rssi'].std(),
                'excellent_count': len(df[df['rssi'] >= -50]),
                'good_count': len(df[(df['rssi'] >= -60) & (df['rssi'] < -50)]),
                'fair_count': len(df[(df['rssi'] >= -70) & (df['rssi'] < -60)]),
                'poor_count': len(df[(df['rssi'] >= -80) & (df['rssi'] < -70)]),
                'dead_count': len(df[df['rssi'] < -80])
            }
            
            coverage_analysis['coverage_stats'][station_name] = rssi_stats
            
            # Identificar zonas mortas
            dead_positions = df[df['rssi'] < -80][['position']].values.tolist()
            if dead_positions:
                coverage_analysis['dead_zones'].extend(dead_positions)
            
            # Identificar excelente cobertura
            excellent_positions = df[df['rssi'] >= -50][['position']].values.tolist()
            if excellent_positions:
                coverage_analysis['excellent_coverage'].extend(excellent_positions)
            
            # Identificar cobertura ruim
            poor_positions = df[(df['rssi'] >= -80) & (df['rssi'] < -70)][['position']].values.tolist()
            if poor_positions:
                coverage_analysis['poor_coverage'].extend(poor_positions)
        
        return coverage_analysis
    
    def generate_heatmap(self, scenario_name: str, save_path: str = None) -> bool:
        """Gera mapa de calor de RSSI para um cenário"""
        if scenario_name not in self.data:
            print(f"❌ Cenário {scenario_name} não encontrado!")
            return False
        
        # Preparar dados para o mapa de calor
        all_positions = []
        all_rssi = []
        
        for station_name, df in self.data[scenario_name].items():
            if 'position' not in df.columns or 'rssi' not in df.columns:
                continue
            
            for _, row in df.iterrows():
                try:
                    # Parse position string "x,y" -> (x, y)
                    pos_str = str(row['position']).strip('"')
                    x, y = map(float, pos_str.split(','))
                    all_positions.append([x, y])
                    all_rssi.append(row['rssi'])
                except:
                    continue
        
        if not all_positions:
            print("❌ Nenhum dado de posição válido encontrado!")
            return False
        
        # Criar grid para interpolação
        positions = np.array(all_positions)
        rssi_values = np.array(all_rssi)
        
        # Definir limites do grid
        x_min, x_max = positions[:, 0].min(), positions[:, 0].max()
        y_min, y_max = positions[:, 1].min(), positions[:, 1].max()
        
        # Criar grid
        grid_size = 50
        x_grid = np.linspace(x_min, x_max, grid_size)
        y_grid = np.linspace(y_min, y_max, grid_size)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # Interpolação simples (média dos pontos próximos)
        Z = np.zeros_like(X)
        for i in range(grid_size):
            for j in range(grid_size):
                # Encontrar pontos próximos
                distances = np.sqrt((positions[:, 0] - X[i, j])**2 + (positions[:, 1] - Y[i, j])**2)
                nearby_indices = distances < (max(x_max - x_min, y_max - y_min) / 10)
                
                if np.any(nearby_indices):
                    Z[i, j] = np.mean(rssi_values[nearby_indices])
                else:
                    Z[i, j] = -100  # Sem dados
        
        # Criar figura
        plt.figure(figsize=(12, 8))
        
        # Mapa de calor
        heatmap = plt.contourf(X, Y, Z, levels=20, cmap='RdYlGn_r')
        plt.colorbar(heatmap, label='RSSI (dBm)')
        
        # Adicionar pontos de dados
        plt.scatter(positions[:, 0], positions[:, 1], c=rssi_values, 
                   cmap='RdYlGn_r', s=50, alpha=0.7, edgecolors='black')
        
        # Configurações
        plt.title(f'Mapa de Calor de RSSI - {scenario_name}', fontsize=16, fontweight='bold')
        plt.xlabel('Posição X (metros)', fontsize=12)
        plt.ylabel('Posição Y (metros)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Adicionar legenda de qualidade
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
                      markersize=10, label='Excelente (-50 a 0 dBm)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', 
                      markersize=10, label='Boa (-60 a -50 dBm)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
                      markersize=10, label='Regular (-70 a -60 dBm)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                      markersize=10, label='Ruim (< -70 dBm)')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Salvar ou mostrar
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Mapa de calor salvo em: {save_path}")
        else:
            plt.show()
        
        plt.close()
        return True
    
    def detect_anomalies(self, scenario_name: str, threshold_std: float = 2.0) -> Dict:
        """Detecta anomalias na rede baseado em desvios estatísticos"""
        if scenario_name not in self.data:
            print(f"❌ Cenário {scenario_name} não encontrado!")
            return {}
        
        anomalies = {
            'scenario': scenario_name,
            'rssi_anomalies': [],
            'latency_anomalies': [],
            'handover_anomalies': [],
            'summary': {}
        }
        
        for station_name, df in self.data[scenario_name].items():
            # Anomalias de RSSI
            if 'rssi' in df.columns:
                rssi_mean = df['rssi'].mean()
                rssi_std = df['rssi'].std()
                rssi_threshold = threshold_std * rssi_std
                
                rssi_outliers = df[abs(df['rssi'] - rssi_mean) > rssi_threshold]
                for _, row in rssi_outliers.iterrows():
                    anomalies['rssi_anomalies'].append({
                        'station': station_name,
                        'position': row.get('position', 'N/A'),
                        'rssi': row['rssi'],
                        'expected_range': f"{rssi_mean - rssi_threshold:.1f} a {rssi_mean + rssi_threshold:.1f}",
                        'deviation': abs(row['rssi'] - rssi_mean)
                    })
            
            # Anomalias de latência
            if 'latency_ms' in df.columns:
                latency_mean = df['latency_ms'].mean()
                latency_std = df['latency_ms'].std()
                latency_threshold = threshold_std * latency_std
                
                latency_outliers = df[abs(df['latency_ms'] - latency_mean) > latency_threshold]
                for _, row in latency_outliers.iterrows():
                    anomalies['latency_anomalies'].append({
                        'station': station_name,
                        'position': row.get('position', 'N/A'),
                        'latency': row['latency_ms'],
                        'expected_range': f"{latency_mean - latency_threshold:.3f} a {latency_mean + latency_threshold:.3f}",
                        'deviation': abs(row['latency_ms'] - latency_mean)
                    })
            
            # Anomalias de handover (mudanças bruscas de RSSI)
            if 'rssi' in df.columns and len(df) > 1:
                rssi_changes = df['rssi'].diff().abs()
                handover_threshold = 20  # dBm
                
                handover_anomalies = df[rssi_changes > handover_threshold]
                for idx, row in handover_anomalies.iterrows():
                    if idx > 0:  # Pular primeira linha (diff = NaN)
                        anomalies['handover_anomalies'].append({
                            'station': station_name,
                            'position': row.get('position', 'N/A'),
                            'rssi_change': rssi_changes[idx],
                            'previous_rssi': df.iloc[idx-1]['rssi'],
                            'current_rssi': row['rssi']
                        })
        
        # Resumo
        anomalies['summary'] = {
            'total_rssi_anomalies': len(anomalies['rssi_anomalies']),
            'total_latency_anomalies': len(anomalies['latency_anomalies']),
            'total_handover_anomalies': len(anomalies['handover_anomalies']),
            'total_anomalies': len(anomalies['rssi_anomalies']) + 
                             len(anomalies['latency_anomalies']) + 
                             len(anomalies['handover_anomalies'])
        }
        
        return anomalies
    
    def generate_performance_report(self, scenario_name: str, output_file: str = None) -> str:
        """Gera relatório completo de performance"""
        if scenario_name not in self.data:
            return "❌ Cenário não encontrado!"
        
        # Análises
        coverage = self.analyze_coverage(scenario_name)
        anomalies = self.detect_anomalies(scenario_name)
        
        # Gerar relatório
        report = f"""
# 📊 Relatório de Performance - {scenario_name}
**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## 📈 Resumo Geral
- **Total de Stations:** {coverage['total_stations']}
- **Total de Anomalias:** {anomalies['summary']['total_anomalies']}
- **Zonas Mortas:** {len(coverage['dead_zones'])}
- **Excelente Cobertura:** {len(coverage['excellent_coverage'])}

## 📊 Análise de Cobertura por Station
"""
        
        for station_name, stats in coverage['coverage_stats'].items():
            report += f"""
### Station: {station_name}
- **RSSI Médio:** {stats['mean']:.1f} dBm
- **RSSI Mín/Máx:** {stats['min']:.1f} / {stats['max']:.1f} dBm
- **Desvio Padrão:** {stats['std']:.1f} dBm
- **Excelente:** {stats['excellent_count']} pontos
- **Boa:** {stats['good_count']} pontos
- **Regular:** {stats['fair_count']} pontos
- **Ruim:** {stats['poor_count']} pontos
- **Sem Sinal:** {stats['dead_count']} pontos
"""
        
        # Anomalias
        report += f"""
## ⚠️ Anomalias Detectadas

### RSSI ({anomalies['summary']['total_rssi_anomalies']} anomalias)
"""
        
        for anomaly in anomalies['rssi_anomalies'][:5]:  # Mostrar apenas 5 primeiras
            report += f"- **{anomaly['station']}** em {anomaly['position']}: {anomaly['rssi']:.1f} dBm (esperado: {anomaly['expected_range']})\n"
        
        if len(anomalies['rssi_anomalies']) > 5:
            report += f"- ... e mais {len(anomalies['rssi_anomalies']) - 5} anomalias\n"
        
        report += f"""
### Latência ({anomalies['summary']['total_latency_anomalies']} anomalias)
"""
        
        for anomaly in anomalies['latency_anomalies'][:5]:
            report += f"- **{anomaly['station']}** em {anomaly['position']}: {anomaly['latency']:.3f} ms (esperado: {anomaly['expected_range']})\n"
        
        if len(anomalies['latency_anomalies']) > 5:
            report += f"- ... e mais {len(anomalies['latency_anomalies']) - 5} anomalias\n"
        
        report += f"""
### Handover ({anomalies['summary']['total_handover_anomalies']} anomalias)
"""
        
        for anomaly in anomalies['handover_anomalies'][:5]:
            report += f"- **{anomaly['station']}** em {anomaly['position']}: mudança de {anomaly['rssi_change']:.1f} dBm ({anomaly['previous_rssi']:.1f} → {anomaly['current_rssi']:.1f})\n"
        
        if len(anomalies['handover_anomalies']) > 5:
            report += f"- ... e mais {len(anomalies['handover_anomalies']) - 5} anomalias\n"
        
        # Recomendações
        report += """
## 💡 Recomendações

"""
        
        if coverage['dead_zones']:
            report += "- ⚠️ **Zonas mortas detectadas:** Considere reposicionar APs ou adicionar mais pontos de acesso\n"
        
        if anomalies['summary']['total_handover_anomalies'] > 0:
            report += "- 🔄 **Handovers bruscos:** Ajuste parâmetros de handover para transições mais suaves\n"
        
        if anomalies['summary']['total_latency_anomalies'] > 0:
            report += "- ⏱️ **Latência instável:** Verifique interferências ou sobrecarga da rede\n"
        
        if not coverage['dead_zones'] and anomalies['summary']['total_anomalies'] == 0:
            report += "- ✅ **Rede estável:** Performance excelente, sem problemas detectados\n"
        
        # Salvar relatório
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Relatório salvo em: {output_file}")
        
        return report
    
    def compare_scenarios(self, scenario_names: List[str]) -> Dict:
        """Compara múltiplos cenários"""
        if len(scenario_names) < 2:
            print("❌ Precisa de pelo menos 2 cenários para comparação!")
            return {}
        
        comparison = {
            'scenarios': scenario_names,
            'coverage_comparison': {},
            'performance_ranking': [],
            'best_scenario': None
        }
        
        # Carregar dados se necessário
        for scenario in scenario_names:
            if scenario not in self.data:
                self.load_data(scenario)
        
        # Comparar cobertura
        for scenario in scenario_names:
            if scenario in self.data:
                coverage = self.analyze_coverage(scenario)
                comparison['coverage_comparison'][scenario] = {
                    'total_stations': coverage['total_stations'],
                    'dead_zones': len(coverage['dead_zones']),
                    'excellent_coverage': len(coverage['excellent_coverage']),
                    'avg_rssi': np.mean([
                        stats['mean'] for stats in coverage['coverage_stats'].values()
                    ]) if coverage['coverage_stats'] else -100
                }
        
        # Ranking de performance
        performance_scores = []
        for scenario, metrics in comparison['coverage_comparison'].items():
            # Score baseado em cobertura e RSSI
            score = (
                metrics['excellent_coverage'] * 10 +  # Excelente cobertura
                (metrics['total_stations'] - metrics['dead_zones']) * 5 +  # Cobertura geral
                max(0, metrics['avg_rssi'] + 100) * 2  # RSSI (normalizado)
            )
            performance_scores.append((scenario, score))
        
        # Ordenar por score
        performance_scores.sort(key=lambda x: x[1], reverse=True)
        comparison['performance_ranking'] = performance_scores
        comparison['best_scenario'] = performance_scores[0][0] if performance_scores else None
        
        return comparison

def main():
    """Função principal para uso via linha de comando"""
    parser = argparse.ArgumentParser(description='Analisador de Performance Avançado')
    parser.add_argument('action', choices=['analyze', 'heatmap', 'anomalies', 'report', 'compare'],
                       help='Ação a executar')
    parser.add_argument('--scenario', '-s', help='Nome do cenário')
    parser.add_argument('--scenarios', '-S', nargs='+', help='Lista de cenários para comparação')
    parser.add_argument('--output', '-o', help='Arquivo de saída')
    parser.add_argument('--results-dir', '-r', default='results', help='Diretório de resultados')
    
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer(args.results_dir)
    
    if args.action == 'analyze':
        if not args.scenario:
            print("❌ Especifique um cenário com --scenario")
            return
        
        analyzer.load_data(args.scenario)
        coverage = analyzer.analyze_coverage(args.scenario)
        print(json.dumps(coverage, indent=2))
    
    elif args.action == 'heatmap':
        if not args.scenario:
            print("❌ Especifique um cenário com --scenario")
            return
        
        analyzer.load_data(args.scenario)
        output_file = args.output or f"heatmap_{args.scenario}.png"
        analyzer.generate_heatmap(args.scenario, output_file)
    
    elif args.action == 'anomalies':
        if not args.scenario:
            print("❌ Especifique um cenário com --scenario")
            return
        
        analyzer.load_data(args.scenario)
        anomalies = analyzer.detect_anomalies(args.scenario)
        print(json.dumps(anomalies, indent=2))
    
    elif args.action == 'report':
        if not args.scenario:
            print("❌ Especifique um cenário com --scenario")
            return
        
        analyzer.load_data(args.scenario)
        output_file = args.output or f"report_{args.scenario}.md"
        report = analyzer.generate_performance_report(args.scenario, output_file)
        print(report)
    
    elif args.action == 'compare':
        if not args.scenarios or len(args.scenarios) < 2:
            print("❌ Especifique pelo menos 2 cenários com --scenarios")
            return
        
        analyzer.load_data()  # Carregar todos
        comparison = analyzer.compare_scenarios(args.scenarios)
        print(json.dumps(comparison, indent=2))

if __name__ == "__main__":
    main() 