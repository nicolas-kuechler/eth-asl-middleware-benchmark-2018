from subprocess import call

# Build Middleware
print("Building Middleware...")
call("ant -buildfile /mnt/c/Users/nicok/eclipse-workspace/asl-fall18-project/build.xml", shell=True)
print("Building Finished")
# Run Middleware
print("Starting Middleware")
call("java -jar /mnt/c/Users/nicok/eclipse-workspace/asl-fall18-project/dist/middleware-kunicola.jar -l localhost -p 6379 -t 10 -s false -m localhost:11211", shell=True)
