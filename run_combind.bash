




TARGET_PROTEIN="thrombin"
echo "Processing $TARGET_PROTEIN"
echo "Processing structures"
combind structprep --root="$TARGET_PROTEIN"

echo "Processing ligands"
combind ligprep "$TARGET_PROTEIN/fragments.csv" --root="$TARGET_PROTEIN/ligands"

echo "Processing docking"
combind dock "$TARGET_PROTEIN/ligands/*/*.maegz" --root="$TARGET_PROTEIN/docking/" --grid "$TARGET_PROTEIN/structures/grids/*/*.zip"

echo "Processing features"
combind featurize "$TARGET_PROTEIN/features" "$TARGET_PROTEIN/docking/*/*_pv.maegz"

echo "Processing pose prediction"
combind pose-prediction "$TARGET_PROTEIN/features" "$TARGET_PROTEIN/poses.csv"
echo "Extracting top poses"
combind extract-top-poses "$TARGET_PROTEIN/poses.csv" "$TARGET_PROTEIN/docking/*/*_pv.maegz"



echo "Entering Virtual Screening"
echo "Processing ligands"
combind ligprep "$TARGET_PROTEIN/library.csv" --multiplex --root="$TARGET_PROTEIN/ligands_vs"
echo "Processing docking"
combind dock "$TARGET_PROTEIN/ligands_vs/library/library.maegz" --screen --grid "$TARGET_PROTEIN/structures/grids/*/*.zip" --root="$TARGET_PROTEIN/docking_vs" --processes=8

echo "Processing features"
combind featurize --screen --max-poses 100000 "$TARGET_PROTEIN/features_screen" "$TARGET_PROTEIN/docking_vs/library-to-thrombin/library-to-thrombin_pv.maegz" "$TARGET_PROTEIN/poses_pv.maegz"

echo "Processing screen"
combind screen "$TARGET_PROTEIN/screen.npy" "$TARGET_PROTEIN/features_screen"

echo "Applying scores"
combind apply-scores "$TARGET_PROTEIN/docking_vs/library-to-thrombin/library-to-thrombin_pv.maegz" "$TARGET_PROTEIN/screen.npy" "$TARGET_PROTEIN/combind_scores_added_pv.maegz"
