import docker
import tempfile
import os
import time

client = docker.from_env()

def run_python_code(source_code: str, input_data: str = "", time_limit: float = 2.0, memory_limit: str = "256m"):
    with tempfile.TemporaryDirectory() as temp_dir:
        code_file_path = os.path.join(temp_dir, "main.py")
        with open(code_file_path, "w") as code_file:
            code_file.write(source_code)
            
        input_file_path = os.path.join(temp_dir, "input.txt")
        with open(input_file_path, "w") as input_file:
            input_file.write(input_data)
        
        try:
            start_time = time.time()
            
            container = client.containers.run(
                image="python:3.12-alpine",
                command='sh -c "python /app/main.py < /app/input.txt"',
                volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                working_dir="/app",
                mem_limit=memory_limit,
                network_disabled=True,
                detach=True
            )
            
            try:
                try:
                    wait_result = container.wait(timeout=time_limit)
                except Exception:
                    return {
                        "status": "TLE",
                        "output": f"Time Limit Exceeded ({time_limit}s)",
                        "runtime": round(time_limit, 3)
                    }

                elapsed_time = round(time.time() - start_time, 3)
                raw_logs = container.logs()
                
                if raw_logs:
                    output_text = raw_logs.decode("utf-8").strip()
                else:
                    output_text = ""
                
                exit_code = wait_result.get("StatusCode", 0)
                
                if exit_code == 0:
                    return {"status": "Success", "output": output_text, "runtime": elapsed_time}
                else:
                    return {"status": "Runtime Error", "output": output_text, "runtime": elapsed_time}
                    
            finally:
                container.remove(force=True)
                
        except Exception as system_error:
            return {"status": "System Error", "output": f"System Error: {str(system_error)}", "runtime": 0}
