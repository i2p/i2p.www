
DOMAINS.keys.each do |domain|
  God.watch do |w|
    w.name="i2p-mirror-#{domain}"
    w.interval=30.seconds
    w.start="/usr/bin/env python app.py #{domain} #{DOMAINS[domain][:port]}"
    w.start_grace=10.seconds
    w.restart_grace=10.seconds
    w.dir=WDIR
    
    w.start_if do |start|
      start.condition(:process_running) do |c|
        c.interval=5.seconds
        c.running=false
      end
    end
    w.restart_if do |restart|
      restart.condition(:memory_usage) do |c|
        c.above=210.megabytes
        c.times=[3,5] # 3 out of 5 intervals
      end
      restart.condition(:cpu_usage) do |c|
        c.above=90.percent
        c.times=7
      end
    end
    
    w.lifecycle do |on|
      on.condition(:flapping) do |c|
        c.to_state = [:start, :restart]
        c.times=5
        c.within=5.minute
        c.transition=:unmonitored
        c.retry_in=10.minutes
        c.retry_times=5
        c.retry_within=2.hours
      end
    end
  end
end
