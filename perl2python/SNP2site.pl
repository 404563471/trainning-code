#!/usr/bin/perl
use strict;
use warnings;
use File::Path qw(make_path remove_tree);
#my $inputfile_SNP = '../hg19_snp/G3.vcf'; #shift;#'test.vcf';
#my $outputdir ='b';# shift; #'b';
#my $need_chrome = 'auto'; #shift ;#'auto';
#my $need_window = 1000000 ;#shift; #1000000;
#my $db_reference_fai = 'hg19.fa.fai';
#my $need_tag = 'Single';

my $inputfile_SNP = shift;#'test.vcf';
my $outputdir = shift; #'b';
my $need_chrome = shift ;#'auto';
my $need_window = shift; #1000000;
my $db_reference_fai = shift;
my $need_tag = shift;

=head1 USAGE
	perl script.pl inputfile_SNP.vcf outputdir all/auto/noY/chr1;chr2;...;chrY 1000000 ucsc.hg19.fasta.fai
	perl <script.pl> <inputfile> <outdir> <chroms> <windows> <sam.fai>
	input file is SNP, and the format:VCF 
=cut

=head1 Contact
	Author : zhihuaPei
	E-mail : zhihuaPei@annoroad.com
	Company : AnnoRoad
=cut

die(`pod2text $0`) if (! $inputfile_SNP || !$outputdir || !$need_chrome || !$need_window);

make_path("$outputdir/data");
make_path("$outputdir/conf");
#判断是否有字段要求
if ($need_tag) {
	die "please enter: Single/Group/SOMATIC \n" if ($need_tag ne 'Single' || $need_tag ne 'Group' || $need_tag ne 'SOMATIC');
}
#判断染色体
my @db_chroms;
foreach  (1..22) {
	push @db_chroms,"chr$_";
}
if ($need_chrome eq 'all') {
	push @db_chroms,"chrX";push @db_chroms,"chrY";
}elsif ($need_chrome eq 'auto') {
	#pass
}elsif ($need_chrome eq 'noY') {
	push @db_chroms,"chrX";
}else {
	@db_chroms = ();
	my @chroms = split/[;|\,]/,$need_chrome;
	foreach  (@chroms) {
		if ($_=~/chr(\d+)/) {
			if ($1>=23) {
				die(`pod2text $0`);
			}else{
				push @db_chroms,$_;
			}
		}elsif ($_ eq 'chrX' || $_ eq 'chrY' ) {
			push @db_chroms,$_;
		}else {
			die(`pod2text $0`);
		}
	}
}
#获取染色体长度
my %hash_db_chromLen = ();
my %hash_window_total_snp = ();
open IN,"<$db_reference_fai" or die $1;
while (<IN>) {
	chomp;
	my @chroms_info = split/\s+/,$_;
	if ($chroms_info[0] =~ /chr\d+$/ || $chroms_info[0] eq 'chrX' || $chroms_info[0] eq 'chrY') {
		$hash_db_chromLen{$chroms_info[0]} = $chroms_info[1];
	}
}
if  (! %hash_db_chromLen) {
	die ('染色体长度文件错误！'."\n");
}
close IN;

#读取SNP文件
my %hash_SNP_VCFinfos = ();
my %hash_SNP_F =();
my %hash_SNP_stat = ();
my %hash_SNP_tag_stat = ();
open IN,"<$inputfile_SNP" or die $!;
while (<IN>) {
	chomp;
	next if $_=~/\#/;
	my @SNP_infos = split /\t/,$_;
	if ($SNP_infos[6] ne 'PASS' || !(exists $hash_db_chromLen{$SNP_infos[0]})) {
		next;
	}
	if ($SNP_infos[3] =~/,/ || $SNP_infos[4] =~/,/) {
		next;
	}
	if ($SNP_infos[0] =~/^chr(.*?)/) {
		#pass
	}else{
		$SNP_infos[0] = 'chr'.$SNP_infos[0];
	}
	my $str_chr = $SNP_infos[0];
	#统计总数
	if (exists $hash_SNP_stat{$str_chr}) {
		$hash_SNP_stat{$str_chr}++;
	}else {
		$hash_SNP_stat{$str_chr} = 1;
	}
	#统计window区间snp数目
	my $region = int($SNP_infos[1] / $need_window) + 1;
	if (exists $hash_window_total_snp{$str_chr}{$region}) {
		$hash_window_total_snp{$str_chr}{$region}++;
	}else{
		$hash_window_total_snp{$str_chr}{$region}=1;
	}
	#如果是单样本 则有关键词：ABHom以及ABHet
	my $tag ;
	if ($SNP_infos[7]=~/ABHet=(.*?);/) {
		#print $1,"\n";
		$tag = 'Single';
		push @{$hash_SNP_VCFinfos{'Single'}{$str_chr}} , [int($SNP_infos[1]),$SNP_infos[1]+10,$1,"fill_color=blue,stroke_color=blue"];
	}elsif ($SNP_infos[7]=~/ABHom=(.*?);/) {
		$tag = 'Single';
		push @{$hash_SNP_VCFinfos{'Single'}{$str_chr}} , [int($SNP_infos[1]),$SNP_infos[1]+10,$1,"fill_color=red,stroke_color=red"]; 
	}elsif ($SNP_infos[7]=~/AF=(.*?);/) {
		$tag = 'Group';
		push @{$hash_SNP_VCFinfos{'Group'}{$str_chr}} ,  [int($SNP_infos[1]),$SNP_infos[1]+10,$1];
	}elsif ($SNP_infos[7]=~/DP=(.*?);/) {
		next if $1<20;
		$tag = 'SOMATIC';
		push @{$hash_SNP_VCFinfos{'SOMATIC'}{$str_chr}} ,[int($SNP_infos[1]),$SNP_infos[1]+10,$1];
	}else{
		die "获取不到字段ABHet or ABHom or AF or DP\n";
	}
	
	if (exists $hash_SNP_F{$str_chr}{$tag}{'MIN'} && $hash_SNP_F{$str_chr}{$tag}{'MAX'}) {
		if ($1 > $hash_SNP_F{$str_chr}{$tag}{'MAX'}) {
			$hash_SNP_F{$str_chr}{$tag}{'MAX'} = $1;
		}
		if ($1 < $hash_SNP_F{$str_chr}{$tag}{'MIN'}) {
			$hash_SNP_F{$str_chr}{$tag}{'MIN'} = $1;
		}
		
	}else {
		$hash_SNP_F{$str_chr}{$tag}{'MIN'} = $1;
		$hash_SNP_F{$str_chr}{$tag}{'MAX'} = $1;
	}
	$hash_SNP_tag_stat{$tag}++;

}
close IN;
#判断字段
if (! $need_tag) {
	($need_tag) = sort {$hash_SNP_tag_stat{$b} <=>$hash_SNP_tag_stat{$a}} keys %hash_SNP_tag_stat;
}
`echo $need_tag>$outputdir/data/snp_tag`;
#输出SNP信息
open OUT,">$outputdir/data/snp.txt" or die $!;
foreach my $key (keys %hash_SNP_VCFinfos) {
	#三种情况
	next if $need_tag ne $key;
	foreach my $key_chr (keys $hash_SNP_VCFinfos{$key}) {
		#SNP
		my $str_chr = $key_chr;
		$str_chr =~s/chr/hs/;
		foreach my $snp (@{$hash_SNP_VCFinfos{$key}{$key_chr}}) {
			if ($key eq 'Single') {
				print OUT "$str_chr\t",join("\t",@$snp),"\n";
			}else{
				my $DP = 0;
				if ($key eq 'Group') {
					$DP = $$snp[2];
				}else{
					$DP = ($$snp[2] - $hash_SNP_F{$key_chr}{$key}{'MIN'}) /($hash_SNP_F{$key_chr}{$key}{'MAX'}-$hash_SNP_F{$key_chr}{$key}{'MIN'});
				}
				if ($DP >= 0.75) {
					print OUT "$str_chr\t$$snp[0]\t$$snp[1]\t$DP\tfill_color=red,stroke_color=red\n";
				}elsif ($DP < 0.25) {
					print OUT "$str_chr\t$$snp[0]\t$$snp[1]\t$DP\tfill_color=green,stroke_color=green\n";
				}else{
					print OUT "$str_chr\t$$snp[0]\t$$snp[1]\t$DP\tfill_color=gray,stroke_color=gray\n";
				}
			}
		}
	}
}
close OUT;
undef %hash_SNP_VCFinfos = ();
undef %hash_SNP_F =();

my @ar_snp_density=();
open OUT,">$outputdir/data/snp.de.txt" or die $!;
foreach my $key_chr (keys %hash_window_total_snp) { #$hash_SNP_stat $hash_db_chromLen
	foreach my $region (sort {$a<=>$b} keys %{$hash_window_total_snp{$key_chr}}) {
		my $str_chr = $key_chr;
		$str_chr =~s/chr/hs/;
		my $start = $need_window * ( $region - 1 ) + 1;
		my $end   = $need_window * ( $region     );
		if ($end > $hash_db_chromLen{$key_chr}) {
			$end = $hash_db_chromLen{$key_chr};
		}
		if (! exists $hash_SNP_F{$str_chr}) {
			$hash_SNP_F{$str_chr}{'MAX'} = $hash_window_total_snp{$key_chr}{$region}/$hash_SNP_stat{$key_chr};
			$hash_SNP_F{$str_chr}{'MIN'} = $hash_window_total_snp{$key_chr}{$region}/$hash_SNP_stat{$key_chr};
		}
		if ( $hash_window_total_snp{$key_chr}{$region}/$hash_SNP_stat{$key_chr} > $hash_SNP_F{$str_chr}{'MAX'}) {
			$hash_SNP_F{$str_chr}{'MAX'} = $hash_window_total_snp{$key_chr}{$region}/$hash_SNP_stat{$key_chr};
		}
		if ( $hash_window_total_snp{$key_chr}{$region}/$hash_SNP_stat{$key_chr} < $hash_SNP_F{$str_chr}{'MIN'}) {
			$hash_SNP_F{$str_chr}{'MIN'} = $hash_window_total_snp{$key_chr}{$region}/$hash_SNP_stat{$key_chr};
		}
		push @ar_snp_density,[$str_chr,$start,$end,$hash_window_total_snp{$key_chr}{$region}/$hash_SNP_stat{$key_chr}];
	}
}
foreach my $key (@ar_snp_density) {
	my $density = 0;
	($hash_SNP_F{$$key[0]}{'MAX'} - $hash_SNP_F{$$key[0]}{'MIN'}) == 0?($density = 0):($density = 
		($$key[3]-$hash_SNP_F{$$key[0]}{'MIN'})/($hash_SNP_F{$$key[0]}{'MAX'} - $hash_SNP_F{$$key[0]}{'MIN'}));
	print OUT "$$key[0]\t$$key[1]\t$$key[2]\t",$density,"\n";
}
close OUT;
undef @ar_snp_density;
exit(0);
