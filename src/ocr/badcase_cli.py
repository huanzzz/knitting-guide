import json
import os
from datetime import datetime
import click
from typing import Dict, List

class SimpleBadCaseManager:
    def __init__(self, badcase_file: str = "badcases.json"):
        self.badcase_file = badcase_file
        self.badcases = self.load_badcases()
    
    def load_badcases(self) -> List[Dict]:
        if os.path.exists(self.badcase_file):
            with open(self.badcase_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_badcases(self):
        with open(self.badcase_file, 'w', encoding='utf-8') as f:
            json.dump(self.badcases, f, ensure_ascii=False, indent=2)
    
    def add_badcase(self, wrong: str, correct: str, error_type: str):
        badcase = {
            "wrong": wrong,
            "correct": correct,
            "type": error_type,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.badcases.append(badcase)
        self.save_badcases()
        self.update_rules()
    
    def list_badcases(self):
        for i, case in enumerate(self.badcases):
            print(f"{i+1}. [{case['type']}] {case['wrong']} -> {case['correct']}")
    
    def update_rules(self):
        """自动更新纠正规则"""
        rules = {
            "term_mapping": {},
            "symbol_mapping": {},
            "number_patterns": []
        }
        
        for case in self.badcases:
            if case['type'] == 'term':
                rules['term_mapping'][case['wrong']] = case['correct']
            elif case['type'] == 'symbol':
                rules['symbol_mapping'][case['wrong']] = case['correct']
            elif case['type'] == 'number':
                rules['number_patterns'].append(case['wrong'])
        
        with open('correction_rules.py', 'w', encoding='utf-8') as f:
            f.write("# 自动生成的纠正规则\n\n")
            f.write("TERM_MAPPING = {\n")
            for wrong, correct in rules['term_mapping'].items():
                f.write(f'    "{wrong}": "{correct}",\n')
            f.write("}\n\n")
            
            f.write("SYMBOL_MAPPING = {\n")
            for wrong, correct in rules['symbol_mapping'].items():
                f.write(f'    "{wrong}": "{correct}",\n')
            f.write("}\n\n")
            
            f.write("NUMBER_PATTERNS = [\n")
            for pattern in rules['number_patterns']:
                f.write(f'    r"{pattern}",\n')
            f.write("]\n")

@click.group()
def cli():
    """简单的BadCase管理工具"""
    pass

@cli.command()
@click.option('--wrong', prompt='错误的文本', help='OCR识别错误的文本')
@click.option('--correct', prompt='正确的文本', help='正确的文本')
@click.option('--type', prompt='错误类型', type=click.Choice(['term', 'symbol', 'number']), help='错误类型：term(术语), symbol(符号), number(数字)')
def add(wrong, correct, type):
    """添加新的badcase"""
    manager = SimpleBadCaseManager()
    manager.add_badcase(wrong, correct, type)
    click.echo(f"已添加: {wrong} -> {correct}")

@cli.command()
def list():
    """列出所有badcase"""
    manager = SimpleBadCaseManager()
    manager.list_badcases()

if __name__ == '__main__':
    cli() 