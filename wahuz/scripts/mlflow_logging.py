import mlflow
import mlflow.sklearn
import os
import argparse
from datetime import datetime
import json

def log_model_metadata(run_id, git_commit, docker_tag):
    """Log model metadata to MLflow"""
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
    
    # Set experiment
    experiment_name = "PDF-QA-Pipeline"
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
    except:
        experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
    
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run(run_name=f"deployment-{run_id}"):
        # Log parameters
        mlflow.log_param("deployment_id", run_id)
        mlflow.log_param("git_commit", git_commit)
        mlflow.log_param("docker_tag", docker_tag)
        mlflow.log_param("deployment_time", datetime.now().isoformat())
        mlflow.log_param("embedding_model", "models/text-embedding-004")
        mlflow.log_param("llm_model", "gemini-1.5-flash")
        
        # Log metrics (these would come from validation)
        mlflow.log_metric("chunk_size", 1000)
        mlflow.log_metric("overlap", 200)
        mlflow.log_metric("top_k", 3)
        
        # Log artifacts
        metadata = {
            "deployment_id": run_id,
            "git_commit": git_commit,
            "docker_tag": docker_tag,
            "timestamp": datetime.now().isoformat(),
            "models": {
                "embedding": "models/text-embedding-004",
                "llm": "gemini-1.5-flash"
            }
        }
        
        with open("deployment_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        mlflow.log_artifact("deployment_metadata.json")
        
        # Set tags
        mlflow.set_tag("stage", "production")
        mlflow.set_tag("model_type", "pdf_qa")
        mlflow.set_tag("framework", "streamlit")
        
        print(f"Logged deployment {run_id} to MLflow")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--docker-tag", required=True)
    
    args = parser.parse_args()
    
    log_model_metadata(args.run_id, args.git_commit, args.docker_tag)
