WARNING - if you can read this you will trust anybody!
The revision containing this file was signed by
untrusted-test@mail.i2p as a test.

Monotone databases may contain untrusted content. Trust in monotone
is enforced ONLY on checkout and update, NOT when syncing with remote databases.

If you are reading this, you will trust anybody -
you should fix this by putting the following
trust hook in your ~/.monotonoe/monotonerc file:

function get_revision_cert_trust(signers, id, name, val)
   local trusted_signers = { "complication@mail.i2p", "zzz@mail.i2p" }
   local t = intersection(signers, trusted_signers)
   if t == nil then return false end
   if table.getn(t) >= 1 then return true end
   return false
end

Edit as you wish to include only the signers YOU trust.

Now, since you can't trust anything in this directory
that you checked out (the directory containing this file),
you should delete the whole thing and check it out again.

You should get a message like:

mtn: warning: trust function disliked 1 signers of branch cert on revision c84b3ecdcf7b2cf7d6091f230bced401613bd5b0

... and you will not see this file.
Now you know your trust hook is working.
