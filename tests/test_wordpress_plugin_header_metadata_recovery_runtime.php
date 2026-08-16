<?php
$path = dirname(__DIR__) . '/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php';
$data = file_get_contents($path, false, null, 0, 8192);
if ($data === false) { fwrite(STDERR, "FAIL - read plugin header\n"); exit(1); }
$headers = array(
  'Plugin Name' => 'Sustainable Catalyst Workspace',
  'Version' => '2.0.0',
  'Author' => 'Content Catalyst LLC',
  'Requires at least' => '6.4',
  'Requires PHP' => '8.0',
);
foreach ($headers as $label => $expected) {
  $pattern = '/^[ \t\/*#@]*' . preg_quote($label, '/') . ':(.*)$/mi';
  if (!preg_match($pattern, $data, $m)) { fwrite(STDERR, "FAIL - missing $label in first 8KB\n"); exit(1); }
  if (trim($m[1]) !== $expected) { fwrite(STDERR, "FAIL - $label mismatch: " . trim($m[1]) . "\n"); exit(1); }
}
echo "PASS - WordPress 8KB plugin header metadata runtime\n";
