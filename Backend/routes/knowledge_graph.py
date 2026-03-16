import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.preprocessing import LabelEncoder
import networkx as nx
from datetime import datetime
import os

# Create output directory for graphs
os.makedirs('kg_graphs', exist_ok=True)

class KnowledgeGraphAnalyzer:
    def __init__(self):
        """Initialize database connection"""
        self.conn = psycopg2.connect(
            dbname="exam_ai_db",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        
    def fetch_data(self):
        """Fetch data from knowledge_graph table"""
        query = """
            SELECT 
                exam,
                subject,
                topic,
                difficulty_score,
                difficulty_label,
                source,
                year,
                confidence
            FROM knowledge_graph
            WHERE difficulty_score IS NOT NULL
            ORDER BY difficulty_score DESC
        """
        return pd.read_sql(query, self.conn)
    
    def fetch_fusion_data(self):
        """Fetch data from analytics_fusion table"""
        query = """
            SELECT 
                exam,
                year,
                fused_difficulty_score as difficulty_score,
                difficulty_label,
                tweet_stress_avg,
                meme_stress_avg,
                paper_difficulty_avg
            FROM analytics_fusion
            WHERE fused_difficulty_score IS NOT NULL
            ORDER BY fused_difficulty_score DESC
        """
        return pd.read_sql(query, self.conn)
    
    def create_decision_tree_graph(self, df, title="Topic Difficulty Decision Tree"):
        """Create decision tree graph for topic difficulty"""
        
        # Prepare data for decision tree
        le_subject = LabelEncoder()
        le_exam = LabelEncoder()
        
        df['subject_encoded'] = le_subject.fit_transform(df['subject'].fillna('General'))
        df['exam_encoded'] = le_exam.fit_transform(df['exam'].fillna('General'))
        
        # Features for decision tree
        X = df[['subject_encoded', 'exam_encoded']].values
        y = df['difficulty_score'].values
        
        # Train decision tree
        dt = DecisionTreeRegressor(max_depth=4, random_state=42)
        dt.fit(X, y)
        
        # Create visualization
        plt.figure(figsize=(20, 12))
        plot_tree(dt, 
                  feature_names=['Subject', 'Exam'],
                  filled=True, 
                  rounded=True,
                  fontsize=10,
                  precision=2)
        
        plt.title(f'{title}\nDecision Tree Analysis of Topic Difficulty', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'kg_graphs/decision_tree_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return dt
    
    def create_subject_wise_topic_graph(self, df):
        """Create subject-wise topic difficulty graphs"""
        
        subjects = df['subject'].unique()
        
        for subject in subjects:
            if pd.isna(subject) or subject == 'General':
                continue
                
            subject_df = df[df['subject'] == subject].sort_values('difficulty_score', ascending=True)
            
            if len(subject_df) < 2:
                continue
                
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'{subject} - Topic Difficulty Analysis', fontsize=16, fontweight='bold')
            
            # 1. Bar Chart - Topics sorted by difficulty
            ax1 = axes[0, 0]
            colors = ['#10b981' if x < 2 else '#f59e0b' if x < 3 else '#ef4444' 
                     for x in subject_df['difficulty_score']]
            bars = ax1.barh(range(len(subject_df)), subject_df['difficulty_score'], color=colors)
            ax1.set_yticks(range(len(subject_df)))
            ax1.set_yticklabels(subject_df['topic'], fontsize=10)
            ax1.set_xlabel('Difficulty Score (1-6)', fontsize=12)
            ax1.set_title(f'Topics from Easiest to Hardest', fontsize=12)
            ax1.set_xlim(0, 6)
            
            # Add value labels
            for i, (bar, score) in enumerate(zip(bars, subject_df['difficulty_score'])):
                ax1.text(score + 0.1, bar.get_y() + bar.get_height()/2, 
                        f'{score:.2f}', va='center', fontsize=9)
            
            # 2. Pie Chart - Difficulty distribution
            ax2 = axes[0, 1]
            diff_counts = subject_df['difficulty_label'].value_counts()
            colors_pie = {'Hard': '#ef4444', 'Medium': '#f59e0b', 'Easy': '#10b981', 
                         'Low': '#10b981', 'High': '#ef4444'}
            pie_colors = [colors_pie.get(x, '#9ca3af') for x in diff_counts.index]
            ax2.pie(diff_counts.values, labels=diff_counts.index, autopct='%1.1f%%',
                   colors=pie_colors, startangle=90)
            ax2.set_title('Difficulty Distribution', fontsize=12)
            
            # 3. Line Chart - Difficulty trend
            ax3 = axes[1, 0]
            subject_df_sorted = subject_df.sort_values('difficulty_score')
            ax3.plot(range(len(subject_df_sorted)), subject_df_sorted['difficulty_score'], 
                    marker='o', linewidth=2, markersize=8, color='#3b82f6')
            ax3.set_xticks(range(len(subject_df_sorted)))
            ax3.set_xticklabels(subject_df_sorted['topic'], rotation=45, ha='right', fontsize=9)
            ax3.set_ylabel('Difficulty Score', fontsize=11)
            ax3.set_title('Difficulty Trend Across Topics', fontsize=12)
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim(0, 6)
            
            # 4. Heatmap-like bar for exam distribution
            ax4 = axes[1, 1]
            exam_counts = subject_df['exam'].value_counts()
            ax4.bar(exam_counts.index, exam_counts.values, color='#8b5cf6', alpha=0.7)
            ax4.set_xlabel('Exam', fontsize=11)
            ax4.set_ylabel('Number of Topics', fontsize=11)
            ax4.set_title('Topics by Exam', fontsize=12)
            ax4.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f'kg_graphs/{subject}_topic_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def create_overall_difficulty_graph(self, df):
        """Create overall difficulty graphs"""
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Overall Topic Difficulty Analysis', fontsize=18, fontweight='bold')
        
        # 1. Top 10 Hardest Topics
        ax1 = axes[0, 0]
        hardest = df.nlargest(10, 'difficulty_score')[['topic', 'subject', 'difficulty_score']]
        colors = ['#ef4444' if i < 3 else '#f59e0b' if i < 7 else '#10b981' 
                 for i in range(len(hardest))]
        bars = ax1.barh(range(len(hardest)), hardest['difficulty_score'], color=colors)
        ax1.set_yticks(range(len(hardest)))
        ax1.set_yticklabels([f"{row['topic']} ({row['subject']})" 
                            for _, row in hardest.iterrows()], fontsize=9)
        ax1.set_xlabel('Difficulty Score', fontsize=12)
        ax1.set_title('Top 10 Hardest Topics', fontsize=13, fontweight='bold')
        ax1.set_xlim(0, 6)
        
        # 2. Top 10 Easiest Topics
        ax2 = axes[0, 1]
        easiest = df.nsmallest(10, 'difficulty_score')[['topic', 'subject', 'difficulty_score']]
        colors = ['#10b981' if i < 3 else '#f59e0b' if i < 7 else '#ef4444' 
                 for i in range(len(easiest))]
        bars = ax2.barh(range(len(easiest)), easiest['difficulty_score'], color=colors)
        ax2.set_yticks(range(len(easiest)))
        ax2.set_yticklabels([f"{row['topic']} ({row['subject']})" 
                            for _, row in easiest.iterrows()], fontsize=9)
        ax2.set_xlabel('Difficulty Score', fontsize=12)
        ax2.set_title('Top 10 Easiest Topics', fontsize=13, fontweight='bold')
        ax2.set_xlim(0, 6)
        
        # 3. Subject-wise Average Difficulty
        ax3 = axes[0, 2]
        subject_avg = df.groupby('subject')['difficulty_score'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        subject_avg = subject_avg[subject_avg['count'] >= 2].head(10)
        
        colors = ['#ef4444' if x > 3.5 else '#f59e0b' if x > 2.5 else '#10b981' 
                 for x in subject_avg['mean']]
        bars = ax3.barh(range(len(subject_avg)), subject_avg['mean'], color=colors)
        ax3.set_yticks(range(len(subject_avg)))
        ax3.set_yticklabels(subject_avg.index, fontsize=10)
        ax3.set_xlabel('Average Difficulty', fontsize=12)
        ax3.set_title('Subject-wise Avg Difficulty', fontsize=13, fontweight='bold')
        ax3.set_xlim(0, 6)
        
        # 4. Difficulty Distribution Pie
        ax4 = axes[1, 0]
        diff_dist = df['difficulty_label'].value_counts()
        colors_pie = {'Hard': '#ef4444', 'Medium': '#f59e0b', 'Easy': '#10b981', 
                     'Low': '#10b981', 'High': '#ef4444'}
        pie_colors = [colors_pie.get(x, '#9ca3af') for x in diff_dist.index]
        ax4.pie(diff_dist.values, labels=diff_dist.index, autopct='%1.1f%%',
               colors=pie_colors, startangle=90)
        ax4.set_title('Overall Difficulty Distribution', fontsize=13, fontweight='bold')
        
        # 5. Difficulty Score Distribution Histogram
        ax5 = axes[1, 1]
        bins = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
        ax5.hist(df['difficulty_score'], bins=bins, color='#3b82f6', alpha=0.7, edgecolor='white')
        ax5.set_xlabel('Difficulty Score', fontsize=12)
        ax5.set_ylabel('Number of Topics', fontsize=12)
        ax5.set_title('Difficulty Score Distribution', fontsize=13, fontweight='bold')
        ax5.axvline(df['difficulty_score'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["difficulty_score"].mean():.2f}')
        ax5.legend()
        
        # 6. Source Distribution
        ax6 = axes[1, 2]
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            ax6.pie(source_counts.values, labels=source_counts.index, autopct='%1.1f%%',
                   colors=['#3b82f6', '#f59e0b', '#10b981'], startangle=90)
            ax6.set_title('Data Source Distribution', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('kg_graphs/overall_difficulty_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_knowledge_network_graph(self, df):
        """Create knowledge graph network visualization"""
        
        G = nx.Graph()
        
        # Add nodes with attributes
        for _, row in df.iterrows():
            # Add exam node
            if pd.notna(row['exam']):
                G.add_node(f"exam_{row['exam']}", type='exam', label=row['exam'])
            
            # Add subject node
            if pd.notna(row['subject']) and row['subject'] != 'General':
                G.add_node(f"subject_{row['subject']}", type='subject', label=row['subject'])
                
            # Add topic node
            if pd.notna(row['topic']) and row['topic'] != 'General':
                node_id = f"topic_{row['topic']}_{row['subject']}"
                G.add_node(node_id, type='topic', label=row['topic'], 
                          difficulty=row['difficulty_score'])
                
                # Add edges
                if pd.notna(row['exam']):
                    G.add_edge(f"exam_{row['exam']}", f"subject_{row['subject']}", 
                              weight=0.5, relation='has_subject')
                
                G.add_edge(f"subject_{row['subject']}", node_id, 
                          weight=row['difficulty_score'], relation='has_topic')
        
        # Create visualization
        plt.figure(figsize=(20, 16))
        
        # Define node colors based on type
        node_colors = []
        for node in G.nodes():
            if 'exam' in node:
                node_colors.append('#ef4444')  # Red for exams
            elif 'subject' in node:
                node_colors.append('#3b82f6')  # Blue for subjects
            else:
                # Topics colored by difficulty
                difficulty = G.nodes[node].get('difficulty', 3)
                if difficulty >= 4:
                    node_colors.append('#ef4444')  # Hard - Red
                elif difficulty >= 2.5:
                    node_colors.append('#f59e0b')  # Medium - Orange
                else:
                    node_colors.append('#10b981')  # Easy - Green
        
        # Calculate node sizes based on degree
        node_sizes = [G.degree(node) * 300 for node in G.nodes()]
        
        # Create layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
        
        # Add labels
        labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        plt.title('Knowledge Graph Network Visualization\n(Red: Exams, Blue: Subjects, Green/Easy, Orange/Medium, Red/Hard for Topics)', 
                 fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('kg_graphs/knowledge_network.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return G
    
    def generate_report(self, df):
        """Generate text report of findings"""
        
        report = []
        report.append("="*80)
        report.append("KNOWLEDGE GRAPH ANALYSIS REPORT")
        report.append("="*80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall statistics
        report.append("📊 OVERALL STATISTICS")
        report.append("-"*40)
        report.append(f"Total Topics: {len(df)}")
        report.append(f"Unique Subjects: {df['subject'].nunique()}")
        report.append(f"Unique Exams: {df['exam'].nunique()}")
        report.append(f"Average Difficulty: {df['difficulty_score'].mean():.2f}")
        report.append(f"Median Difficulty: {df['difficulty_score'].median():.2f}")
        report.append(f"Std Deviation: {df['difficulty_score'].std():.2f}")
        report.append("")
        
        # Difficulty distribution
        report.append("📈 DIFFICULTY DISTRIBUTION")
        report.append("-"*40)
        diff_counts = df['difficulty_label'].value_counts()
        for label, count in diff_counts.items():
            percentage = (count/len(df))*100
            report.append(f"{label}: {count} topics ({percentage:.1f}%)")
        report.append("")
        
        # Top 10 hardest topics
        report.append("🔥 TOP 10 HARDEST TOPICS")
        report.append("-"*40)
        hardest = df.nlargest(10, 'difficulty_score')[['subject', 'topic', 'difficulty_score']]
        for i, (_, row) in enumerate(hardest.iterrows(), 1):
            report.append(f"{i}. {row['subject']} - {row['topic']}: {row['difficulty_score']:.2f}")
        report.append("")
        
        # Top 10 easiest topics
        report.append("✅ TOP 10 EASIEST TOPICS")
        report.append("-"*40)
        easiest = df.nsmallest(10, 'difficulty_score')[['subject', 'topic', 'difficulty_score']]
        for i, (_, row) in enumerate(easiest.iterrows(), 1):
            report.append(f"{i}. {row['subject']} - {row['topic']}: {row['difficulty_score']:.2f}")
        report.append("")
        
        # Subject-wise analysis
        report.append("📚 SUBJECT-WISE ANALYSIS")
        report.append("-"*40)
        subject_stats = df.groupby('subject').agg({
            'difficulty_score': ['mean', 'min', 'max', 'count']
        }).round(2).sort_values(('difficulty_score', 'mean'), ascending=False)
        
        for subject in subject_stats.index[:10]:  # Top 10 subjects
            stats = subject_stats.loc[subject]
            report.append(f"\n{subject}:")
            report.append(f"  • Topics: {stats[('difficulty_score', 'count')]}")
            report.append(f"  • Avg Difficulty: {stats[('difficulty_score', 'mean')]}")
            report.append(f"  • Range: {stats[('difficulty_score', 'min')]} - {stats[('difficulty_score', 'max')]}")
        report.append("")
        
        # Exam-wise analysis
        report.append("🎯 EXAM-WISE ANALYSIS")
        report.append("-"*40)
        exam_stats = df.groupby('exam').agg({
            'difficulty_score': ['mean', 'min', 'max', 'count']
        }).round(2).sort_values(('difficulty_score', 'mean'), ascending=False)
        
        for exam in exam_stats.index[:10]:  # Top 10 exams
            stats = exam_stats.loc[exam]
            report.append(f"\n{exam}:")
            report.append(f"  • Topics: {stats[('difficulty_score', 'count')]}")
            report.append(f"  • Avg Difficulty: {stats[('difficulty_score', 'mean')]}")
            report.append(f"  • Range: {stats[('difficulty_score', 'min')]} - {stats[('difficulty_score', 'max')]}")
        
        report.append("")
        report.append("="*80)
        
        # Save report to file
        with open('kg_graphs/analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return '\n'.join(report)
    
    def run_full_analysis(self):
        """Run complete analysis and generate all graphs"""
        
        print("🔄 Fetching data from database...")
        df = self.fetch_data()
        df_fusion = self.fetch_fusion_data()
        
        # Combine data if needed
        if len(df_fusion) > 0:
            df_fusion['source'] = 'fusion'
            df = pd.concat([df, df_fusion], ignore_index=True, sort=False)
        
        print(f"✅ Fetched {len(df)} records")
        print("\n" + "="*80)
        
        # 1. Generate report
        print("📝 Generating analysis report...")
        report = self.generate_report(df)
        print(report)
        
        # 2. Create decision tree
        print("\n🌳 Creating decision tree graph...")
        self.create_decision_tree_graph(df)
        
        # 3. Create subject-wise graphs
        print("\n📊 Creating subject-wise topic graphs...")
        self.create_subject_wise_topic_graph(df)
        
        # 4. Create overall difficulty graphs
        print("\n📈 Creating overall difficulty analysis...")
        self.create_overall_difficulty_graph(df)
        
        # 5. Create knowledge network
        print("\n🕸️ Creating knowledge network visualization...")
        self.create_knowledge_network_graph(df)
        
        print("\n✅ Analysis complete! All graphs saved to 'kg_graphs' directory")
        print("\n📁 Generated files:")
        for file in os.listdir('kg_graphs'):
            print(f"   • {file}")
        
        return df

def main():
    """Main function to run the analysis"""
    
    print("="*80)
    print("📊 KNOWLEDGE GRAPH ANALYSIS SUITE")
    print("="*80)
    print("\nThis tool will generate:")
    print("  • Decision tree graphs for topic difficulty")
    print("  • Subject-wise topic analysis charts")
    print("  • Overall difficulty distribution")
    print("  • Knowledge network visualization")
    print("  • Comprehensive text report")
    print("\n" + "="*80)
    
    # Run analysis
    analyzer = KnowledgeGraphAnalyzer()
    df = analyzer.run_full_analysis()
    
    # Additional: Export to CSV
    df.to_csv('kg_graphs/knowledge_graph_data.csv', index=False)
    print("\n✅ Data exported to 'kg_graphs/knowledge_graph_data.csv'")

if __name__ == "__main__":
    main()