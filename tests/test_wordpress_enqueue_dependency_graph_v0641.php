<?php
$root = dirname(__DIR__);
$source = file_get_contents($root . '/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php');
if ($source === false) { fwrite(STDERR, "FAIL - source unavailable\n"); exit(1); }
$pattern = "/wp_enqueue_script\\(\\s*'([^']+)'\\s*,.*?\\n\\s*array\\((.*?)\\)\\s*,\\s*SC_WORKSPACE_VERSION\\s*,\\s*(?:true|false)\\s*\\);/s";
preg_match_all($pattern, $source, $matches, PREG_SET_ORDER);
$graph = [];
foreach ($matches as $m) {
    $handle = $m[1];
    preg_match_all("/'([^']+)'/", $m[2], $deps);
    $graph[$handle] = $deps[1];
    if (in_array($handle, $deps[1], true)) {
        fwrite(STDERR, "FAIL - self dependency: {$handle}\n"); exit(1);
    }
}
if (!isset($graph['sc-workspace-accessibility-v1'])) { fwrite(STDERR, "FAIL - accessibility enqueue missing\n"); exit(1); }
if ($graph['sc-workspace-accessibility-v1'] !== ['sc-workspace-browser-compatibility-v1']) { fwrite(STDERR, "FAIL - accessibility dependency contract\n"); exit(1); }
$visiting=[];$visited=[];
$walk = function($node) use (&$walk,&$graph,&$visiting,&$visited) {
    if (isset($visited[$node])) return;
    if (isset($visiting[$node])) { fwrite(STDERR, "FAIL - dependency cycle at {$node}\n"); exit(1); }
    $visiting[$node]=true;
    foreach (($graph[$node] ?? []) as $dep) if (isset($graph[$dep])) $walk($dep);
    unset($visiting[$node]);$visited[$node]=true;
};
foreach (array_keys($graph) as $node) $walk($node);
echo 'PASS - v0.64.1 WordPress enqueue dependency graph' . PHP_EOL;
