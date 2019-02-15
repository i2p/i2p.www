{% trans -%}
============================
NTCP2 implementation details
============================
{%- endtrans %}

.. meta::
    :author: villain
    :date: 2018-08-20
    :category: development
    :excerpt: {% trans %}I2P's new transport protocol implementation details{% endtrans %}

{% trans -%}
    `Source article`_ by orignal at habr.com

{%- endtrans %}

.. _`Source article`: https://habr.com/post/416785/

{% trans -%}
I2P's transport protocols were originally developed around 15 years ago. Back 
then, the main goal was to hide the transferred data, not to hide the fact that 
one was using the protocol itself. Nobody thought seriously about protecting 
against DPI (deep packets inspection) and protocols censorship. Times change, 
and even though original transport protocols are still providing strong security, 
there was a demand for a new transport protocol. NTCP2 is designed to resist 
current censorship threats. Mainly, DPI analysis of packets length. Plus, the new 
protocol uses the most modern cryptography developments. NTCP2 is based on the 
`Noise Protocol Framework`_, with SHA256 
as a hash function and x25519 as an elliptic curve Diffie-Hellman (DH) key 
exchange.
{%- endtrans %}

.. _`Noise Protocol Framework`: https://noiseprotocol.org/noise.html


{% trans -%}
Full specification of NTCP2 protocol can be `found here`_.
{%- endtrans %}

.. _`found here`: {{ spec_url('ntcp2') }}

{% trans -%}
New crypto
----------
{%- endtrans %}

{% trans -%}
NTCP2 requires adding the next cryptographic algorithms to an I2P implementation:
{%- endtrans %}

- x25519
- HMAC-SHA256
- Chacha20
- Poly1305
- AEAD
- SipHash

{% trans -%}
Compared to our original protocol, NTCP, NTCP2 uses x25519 instead of ElGamal 
for DH function, AEAD/Chaha20/Poly1305 instead of AES-256-CBC/Adler32, and uses 
SipHash for obfuscating the packet's length information. The key derivation 
function used in NTCP2 is more complex, now using many HMAC-SHA256 calls.
{%- endtrans %}

{% trans -%}
i2pd (C++) implementation note: All of the algorithms mentioned above, except 
SipHash, are implemented in OpenSSL 1.1.0. SipHash will be added to the coming 
OpenSSL 1.1.1 release. For compatibility with OpenSSL 1.0.2, which is used in 
most of the current systems, core i2pd developer 
`Jeff Becker`_ has contributed standalone 
implementations of missing cryptographic algorithms. 
{%- endtrans %}

.. _`Jeff Becker`: https://github.com/majestrate

{% trans -%}
RouterInfo changes
------------------
{%- endtrans %}

{% trans -%}
NTCP2 requires having a third (x25519) key in addition to existing two (the 
encryption and signature keys). It is called a static key and it has to be added 
to any of RouterInfo addresses as an "s" parameter. It is required for both 
NTCP2 initiator (Alice) and responder (Bob). If more than one address supports 
NTCP2, for example, IPv4 and IPv6, "s" is required to be the same for all of 
them. Alice's address is allowed to have just the "s" parameter without "host" 
and "port" set. Also, a "v" parameter is required, that is currently always set 
to "2".
{%- endtrans %}

{% trans -%}
NTCP2 address can be declared as a separate NTCP2 address or as an old-style 
NTCP address with additional parameters, in which case it will accept both 
NTCP and NTCP2 connections. Java I2P implementation uses the second approach, 
i2pd (C++ implementation) uses the first.
{%- endtrans %}

{% trans -%}
If a node accepts NTCP2 connections, it has to publish its RouterInfo with the 
"i" parameter, which is used as an initialization vector (IV) for the public 
encryption key when that node establishes new connections.
{%- endtrans %}

{% trans -%}
Establishing a connection
-------------------------
{%- endtrans %}

{% trans -%}
To establish a connection both sides need to generate pairs of ephemeral x25519 
keys. Based on those keys and "static" keys they derive a set of keys for data 
transferring. Both parties must verify that the other side actually has a 
private key for that static key, and that static key is the same as in RouterInfo.
{%- endtrans %}

{% trans -%}
Three messages are being sent to establish a connection:
{%- endtrans %}

::

    Alice                           Bob
      
    SessionRequest ------------------->
    <------------------- SessionCreated
    SessionConfirmed ----------------->


{% trans -%}
A common x25519 key, called «input key material», is computed for each message, 
after which message encryption key is generated with a MixKey function. A value 
ck (chaining key) is kept while messages are being exchanged. 
That value is used as a final input when generating keys for data transferring. 
{%- endtrans %}

{% trans -%}
MixKey function looks something like this in the C++ implementation of I2P:
{%- endtrans %}

::

    void NTCP2Establisher::MixKey (const uint8_t * inputKeyMaterial, uint8_t * derived)
    {
            // temp_key = HMAC-SHA256(ck, input_key_material)
            uint8_t tempKey[32]; unsigned int len;
            HMAC(EVP_sha256(), m_CK, 32, inputKeyMaterial, 32, tempKey, &len); 	
            // ck = HMAC-SHA256(temp_key, byte(0x01)) 
            static uint8_t one[1] =  { 1 };
            HMAC(EVP_sha256(), tempKey, 32, one, 1, m_CK, &len); 	
            // derived = HMAC-SHA256(temp_key, ck || byte(0x02))
            m_CK[32] = 2;
            HMAC(EVP_sha256(), tempKey, 32, m_CK, 33, derived, &len); 	
    }



{% trans -%}
**SessionRequest** message is made of a public x25519 Alice key (32 bytes), a 
block of data encrypted with AEAD/Chacha20/Poly1305 (16 bytes), a hash 
(16 bytes) and some random data in the end (padding). Padding length is 
defined in the encrypted block of data. Encrypted block also contains length of 
the second part of the **SessionConfirmed** message. A block of data is 
encrypted and signed with a key derived from Alice's ephemeral key and 
Bob's static key. Initial ck value for MixKey function is set to SHA256 
(Noise_XKaesobfse+hs2+hs3_25519_ChaChaPoly_SHA256).
{%- endtrans %}

{% trans -%}
Since 32 bytes of public x25519 key can be detected by DPI, it is encrypted with 
AES-256-CBC algorithm using hash of Bob's address as a key and "i" parameter 
from RouterInfo as an initialization vector (IV).
{%- endtrans %}

{% trans -%}
**SessionCreated** message has the same structure as **SessionRequest**, except 
the key is computed based on ephemeral keys of both sides. IV generated after 
encrypting/decrypting public key from **SessionRequest** message is used as IV 
for encrypting/decrypting ephemeral public key.
{%- endtrans %}

{% trans -%}
**SessionConfirmed** message has 2 parts: public static key and Alice's 
RouterInfo. The difference from previous messages is that ephemeral public key 
is encrypted with AEAD/Chaha20/Poly1305 using the same key as **SessionCreated**. 
It leads to increasing first part of the message from 32 to 48 bytes. 
The second part is also encrypted with AEAD/Chaha20/Poly1305, but using a new 
key, computed from Bob's ephemeral key and Alice's static key. RouterInfo part 
can also be appended with random data padding, but it is not required, since 
RouterInfo usually has various length.
{%- endtrans %}

{% trans -%}
Generation of data transfer keys
--------------------------------
{%- endtrans %}

{% trans -%}
If every hash and key verification has succeeded, a common ck value must be 
present after the last MixKey operation on both sides. This value is used to 
generate two sets of keys <k, sipk, sipiv> for each side of a connection. "k" is 
a AEAD/Chaha20/Poly1305 key, "sipk" is a SipHash key, "sipiv" is an initial 
value for SipHash IV, that is changed after each use.
{%- endtrans %}

{% trans -%}
Code used to generate keys looks like this in the C++ implementation of I2P:
{%- endtrans %}


::

    void NTCP2Session::KeyDerivationFunctionDataPhase ()
    {
            uint8_t tempKey[32]; unsigned int len;
            // temp_key = HMAC-SHA256(ck, zerolen)
            HMAC(EVP_sha256(), m_Establisher->GetCK (), 32, nullptr, 0, tempKey, &len); 
            static uint8_t one[1] =  { 1 };
            // k_ab = HMAC-SHA256(temp_key, byte(0x01)).
            HMAC(EVP_sha256(), tempKey, 32, one, 1, m_Kab, &len); 
            m_Kab[32] = 2;
            // k_ba = HMAC-SHA256(temp_key, k_ab || byte(0x02))
            HMAC(EVP_sha256(), tempKey, 32, m_Kab, 33, m_Kba, &len);  
            static uint8_t ask[4] = { 'a', 's', 'k', 1 }, master[32];
            // ask_master = HMAC-SHA256(temp_key, "ask" || byte(0x01))
            HMAC(EVP_sha256(), tempKey, 32, ask, 4, master, &len); 
            uint8_t h[39];
            memcpy (h, m_Establisher->GetH (), 32);
            memcpy (h + 32, "siphash", 7);
            // temp_key = HMAC-SHA256(ask_master, h || "siphash")
            HMAC(EVP_sha256(), master, 32, h, 39, tempKey, &len); 
            // sip_master = HMAC-SHA256(temp_key, byte(0x01))  
            HMAC(EVP_sha256(), tempKey, 32, one, 1, master, &len); 
            // temp_key = HMAC-SHA256(sip_master, zerolen)
            HMAC(EVP_sha256(), master, 32, nullptr, 0, tempKey, &len); 
           // sipkeys_ab = HMAC-SHA256(temp_key, byte(0x01)).
            HMAC(EVP_sha256(), tempKey, 32, one, 1, m_Sipkeysab, &len); 
            m_Sipkeysab[32] = 2;
             // sipkeys_ba = HMAC-SHA256(temp_key, sipkeys_ab || byte(0x02)) 
            HMAC(EVP_sha256(), tempKey, 32, m_Sipkeysab, 33, m_Sipkeysba, &len);
    }



{% trans -%}
i2pd (C++) implementation note: First 16 bytes of the "sipkeys" array are a 
SipHash key, the last 8 bytes are IV. SipHash requires two 8 byte keys, but i2pd 
handles them as a single 16 bytes key.
{%- endtrans %}

{% trans -%}
Data transferring
-----------------
{%- endtrans %}

{% trans -%}
Data is transferred in frames, each frame has 3 parts:
{%- endtrans %}

{% trans -%}
- 2 bytes of frame length obfuscated with SipHash
- data encrypted with Chacha20
- 16 bytes of Poly1305 hash value
{%- endtrans %}

{% trans -%}
Maximum length of data transferred in one frame is 65519 bytes.
{%- endtrans %}

{% trans -%}
Message length is obfuscated by applying the XOR function with two first bytes 
of the current SipHash IV.
{%- endtrans %}

{% trans -%}
Encrypted data part contains blocks of data. Each block is prepended with 3 
bytes header, that defines block type and block length. Generally, I2NP type 
blocks are transferred, that are I2NP messages with an altered header. One NTCP2 
frame can transfer multiple I2NP blocks.
{%- endtrans %}

{% trans -%}
The other important data block type is a random data block. It is recommended to 
add a random data block to every NTCP2 frame. Only one random data block can be 
added and it must be the last block.
{%- endtrans %}

{% trans -%}
Those are other data blocks used in the current NTCP2 implementation:
{%- endtrans %}

{% trans -%}
- RouterInfo  — usually contains Bob's RouterInfo after the connection has been established, but it can also contain RouterInfo of a random node for the purpose of speeding up floodfills (there is a flags field for that case). 
- Termination  — is used when a host explicitly terminates a connection and specifies a reason for that.
- DateTime — a current time in seconds.

{%- endtrans %}

{% trans -%}
Summary
-------
{%- endtrans %}

{% trans -%}
The new I2P transport protocol NTCP2 provides effective resistance against DPI 
censorship. It also results in reduced CPU load because of the faster, modern 
cryptography used. It makes I2P more likely to run on low-end devices, such as 
smartphones and home routers. Both major I2P implementations have full support 
for NTCP2 and it make NTCP2 available for use starting with version 
0.9.36 (Java) and 2.20 (i2pd, C++). 
{%- endtrans %}
