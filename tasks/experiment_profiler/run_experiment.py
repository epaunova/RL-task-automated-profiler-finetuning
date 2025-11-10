import yaml
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from ..api.claude_client import ClaudeClient
from ..evaluation.grader import ResponseGrader

class ExperimentRunner:
    def __init__(self, config_path: str, data_path: str, output_dir: str = "results"):
        self.config_path = Path(config_path)
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Validate paths exist
        self._validate_paths()
        
        self.load_config()
        self.load_data()
        self.setup_logging()
        
        self.client = ClaudeClient()
        self.grader = ResponseGrader()
    
    def _validate_paths(self):
        """Validate that required paths exist"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
    
    def load_config(self):
        """Load and validate experiment configuration from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        
        self.experiments = self.config.get('experiments', {})
        
        if not self.experiments:
            raise ValueError("No experiments found in configuration")
    
    def load_data(self):
        """Load and validate sample dialogs data"""
        try:
            with open(self.data_path, 'r') as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")
        
        self.dialogs = self.data.get('dialogs', [])
        
        if not self.dialogs:
            raise ValueError("No dialogs found in data file")
    
    def validate_experiment_config(self, config: Dict[str, Any]) -> bool:
        """Validate experiment configuration has required fields"""
        required_fields = ['model', 'temperature', 'max_tokens']
        for field in required_fields:
            if field not in config:
                self.logger.error(f"Missing required field in config: {field}")
                return False
        
        # Validate temperature range
        temp = config.get('temperature', 0.7)
        if not (0.0 <= temp <= 1.0):
            self.logger.error(f"Temperature must be between 0.0 and 1.0, got: {temp}")
            return False
        
        # Validate max_tokens
        max_tokens = config.get('max_tokens', 1024)
        if max_tokens <= 0:
            self.logger.error(f"max_tokens must be positive, got: {max_tokens}")
            return False
            
        return True
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.output_dir / f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_experiment(self, experiment_name: str) -> Dict[str, Any]:
        """Run specific experiment by name"""
        if experiment_name not in self.experiments:
            raise ValueError(f"Experiment '{experiment_name}' not found in config")
        
        experiment_config = self.experiments[experiment_name]
        
        # Validate config before running
        if not self.validate_experiment_config(experiment_config):
            raise ValueError(f"Invalid configuration for experiment: {experiment_name}")
        
        self.logger.info(f"Starting experiment: {experiment_name}")
        self.logger.info(f"Configuration: {experiment_config}")
        
        prompts = [dialog['prompt'] for dialog in self.dialogs]
        expected_facts = [dialog.get('expected_facts', []) for dialog in self.dialogs]
        
        # Run API requests
        results = self.client.batch_request(prompts, experiment_config)
        
        # Evaluate responses
        evaluation_results = []
        for i, (result, facts) in enumerate(zip(results, expected_facts)):
            if result['success']:
                score = self.grader.evaluate_coverage(result['content'], facts)
                evaluation_results.append({
                    'prompt_id': i,
                    'response': result['content'],
                    'score': score,
                    'coverage': score['coverage_percentage'],
                    'usage': result['usage'],
                    'success': True
                })
                self.logger.info(f"Prompt {i}: Coverage {score['coverage_percentage']:.1f}%")
            else:
                evaluation_results.append({
                    'prompt_id': i,
                    'response': '',
                    'score': {'coverage_percentage': 0, 'matched_facts': []},
                    'coverage': 0,
                    'error': result['error'],
                    'success': False
                })
                self.logger.error(f"Prompt {i}: API Error - {result['error']}")
        
        # Calculate overall metrics
        successful_runs = [r for r in evaluation_results if r['success']]
        if successful_runs:
            avg_coverage = sum(r['coverage'] for r in successful_runs) / len(successful_runs)
            total_tokens = sum(r['usage'].get('total_tokens', 0) for r in successful_runs)
        else:
            avg_coverage = 0
            total_tokens = 0
        
        experiment_result = {
            'experiment_name': experiment_name,
            'config_used': experiment_config,
            'timestamp': datetime.now().isoformat(),
            'total_prompts': len(prompts),
            'successful_responses': len(successful_runs),
            'average_coverage': avg_coverage,
            'total_tokens_used': total_tokens,
            'detailed_results': evaluation_results
        }
        
        # Save results
        self.save_results(experiment_name, experiment_result)
        
        self.logger.info(f"Experiment completed: {avg_coverage:.1f}% average coverage")
        
        return experiment_result
    
    def save_results(self, experiment_name: str, results: Dict[str, Any]):
        """Save experiment results to file"""
        output_file = self.output_dir / f"{experiment_name}_results.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Results saved to: {output_file}")
    
    def list_experiments(self) -> List[str]:
        """List available experiments"""
        return list(self.experiments.keys())
