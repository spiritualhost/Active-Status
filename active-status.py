import subprocess, math

def heartbeat(period_remaining: float):
    print(f"The period remaining is {period_remaining}.\n")
    return

commands = """
$product = (Get-WmiObject -Query "SELECT * FROM SoftwareLicensingProduct WHERE PartialProductKey IS NOT NULL")
$product.GracePeriodRemaining
"""

if __name__ == "__main__":
    print("Test")
    result = subprocess.run(
        ["powershell", "-Command", commands],
        capture_output=True,
        text=True)
    
    raw_period = result.stdout

    period_remaining = float(raw_period) if raw_period != "0\n0\n" else math.inf  

    print(type(period_remaining))
    print(period_remaining)

    #Heartbeat to SQL server
    heartbeat(period_remaining)